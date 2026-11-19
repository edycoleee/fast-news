from app.core.config import settings


def test_readiness_checks_database(client) -> None:
    response = client.get('/api/readiness')

    assert response.status_code == 200
    assert response.json() == {'status': 'ready', 'database': 'connected'}
    assert response.headers.get('x-correlation-id')


def test_audit_log_login_success_and_export(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='audit.read',
        resource='audit',
        action='read',
    )
    login_response = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )
    assert login_response.status_code == 200

    logs_response = client.get('/api/audit/logs?action=auth.login')
    assert logs_response.status_code == 200
    assert any(item['action'] == 'auth.login.success' for item in logs_response.json()['items'])

    export_response = client.get('/api/audit/logs/export?action=auth.login')
    assert export_response.status_code == 200
    assert export_response.headers['content-type'].startswith('text/csv')
    assert 'auth.login.success' in export_response.text


def test_audit_log_forbidden_without_permission(client, create_user) -> None:
    create_user()
    client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )

    response = client.get('/api/audit/logs')

    assert response.status_code == 403
