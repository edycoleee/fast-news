from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.rate_limit_bucket import RateLimitBucket
from conftest import TestSessionLocal, _run_async


def login(client, username='admin', password='StrongPass123!'):
    return client.post(
        '/api/auth/login',
        json={'username_or_email': username, 'password': password},
    )


def login_with_csrf(client):
    response = login(client)
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def setup_settings_admin(create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='settings.manage',
        resource='settings',
        action='manage',
    )


def create_old_retention_data() -> None:
    async def _create() -> None:
        async with TestSessionLocal() as session:
            now = datetime.utcnow()
            session.add(
                AuditLog(
                    action='test.old',
                    entity_type='test',
                    created_at=now - timedelta(days=400),
                )
            )
            session.add(
                RateLimitBucket(
                    scope='test',
                    identifier='127.0.0.1',
                    window_start=now - timedelta(days=10),
                    count=1,
                )
            )
            await session.commit()

    _run_async(_create())


def test_settings_require_permission(client, create_user) -> None:
    create_user()
    login_with_csrf(client)

    response = client.get('/api/settings')

    assert response.status_code == 403


def test_settings_update_enforces_hard_caps_and_audit(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_settings_admin(create_user, assign_permission_to_user)
    csrf_token = login_with_csrf(client)

    invalid_response = client.put(
        '/api/settings',
        json={
            'settings': [
                {
                    'key': 'upload.max_size_bytes',
                    'value': settings.UPLOAD_HARD_CAP_BYTES + 1,
                }
            ]
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert invalid_response.status_code == 422

    valid_response = client.put(
        '/api/settings',
        json={
            'settings': [
                {'key': 'upload.max_size_bytes', 'value': 10 * 1024 * 1024},
                {'key': 'comment.rate_limit_per_hour', 'value': 5},
            ]
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert valid_response.status_code == 200
    values = {item['key']: item['value'] for item in valid_response.json()['items']}
    assert values['upload.max_size_bytes'] == 10 * 1024 * 1024
    assert values['comment.rate_limit_per_hour'] == 5

    public_response = client.get('/api/settings/public')
    assert public_response.status_code == 200
    assert public_response.json()['upload_max_size_bytes'] == 10 * 1024 * 1024


def test_login_failure_threshold_triggers_temporary_lock(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_settings_admin(create_user, assign_permission_to_user)
    csrf_token = login_with_csrf(client)
    update_response = client.put(
        '/api/settings',
        json={
            'settings': [
                {'key': 'login.rate_limit_per_minute', 'value': 10},
                {'key': 'login.failure_threshold', 'value': 3},
                {'key': 'login.cooldown_seconds', 'value': 60},
            ]
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert update_response.status_code == 200
    client.post(
        '/api/auth/logout',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )

    for _ in range(3):
        response = client.post(
            '/api/auth/login',
            json={'username_or_email': 'admin', 'password': 'WrongPassword123!'},
        )
        assert response.status_code == 401

    locked_response = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin', 'password': 'StrongPass123!'},
    )
    assert locked_response.status_code == 429
    assert locked_response.headers['retry-after'] == '60'


def test_dynamic_comment_limit_is_authoritative(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_settings_admin(create_user, assign_permission_to_user)
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_with_csrf(client)
    update_response = client.put(
        '/api/settings',
        json={'settings': [{'key': 'comment.max_length', 'value': 100}]},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert update_response.status_code == 200
    news_response = client.post(
        '/api/news',
        json={
            'title': 'Security setting test',
            'slug': 'security-setting-test',
            'summary': 'Runtime limits',
            'content': '<p>Runtime settings test.</p>',
            'status': 'published',
            'category_id': None,
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert news_response.status_code == 201

    comment_response = client.post(
        '/api/public/news/security-setting-test/comments',
        json={
            'author_name': 'Reader',
            'content': 'x' * 101,
            'parent_id': None,
        },
    )
    assert comment_response.status_code == 422


def test_retention_cleanup_requires_permission(client, create_user) -> None:
    create_user()
    csrf_token = login_with_csrf(client)

    response = client.post(
        '/api/settings/retention/cleanup',
        json={'dry_run': True, 'batch_size': 50},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )

    assert response.status_code == 403


def test_retention_cleanup_manual_trigger(client, create_user, assign_permission_to_user) -> None:
    setup_settings_admin(create_user, assign_permission_to_user)
    csrf_token = login_with_csrf(client)
    create_old_retention_data()

    dry_run_response = client.post(
        '/api/settings/retention/cleanup',
        json={'dry_run': True, 'batch_size': 10},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert dry_run_response.status_code == 200
    dry_run_data = dry_run_response.json()
    assert dry_run_data['dry_run'] is True
    assert dry_run_data['eligible']['audit_logs'] == 1
    assert dry_run_data['deleted']['audit_logs'] == 0

    cleanup_response = client.post(
        '/api/settings/retention/cleanup',
        json={'dry_run': False, 'batch_size': 10},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert cleanup_response.status_code == 200
    cleanup_data = cleanup_response.json()
    assert cleanup_data['dry_run'] is False
    assert cleanup_data['deleted']['audit_logs'] == 1
    assert cleanup_data['deleted']['rate_limit_buckets'] == 1

    followup_response = client.post(
        '/api/settings/retention/cleanup',
        json={'dry_run': True, 'batch_size': 10},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert followup_response.status_code == 200
    assert followup_response.json()['eligible']['audit_logs'] == 0

    async def _count_cleanup_audits() -> int:
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(AuditLog).where(AuditLog.action == 'retention.cleanup')
            )
            return len(list(result.scalars().all()))

    assert _run_async(_count_cleanup_audits()) == 1
