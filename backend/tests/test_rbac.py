from app.core.config import settings
from app.modules.rbac.permission_registry import (
    get_registered_permission_names,
    get_registered_permissions,
)


def login_as_admin(client):
    response = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def test_rbac_create_role_forbidden_without_permission(client, create_user) -> None:
    create_user()
    csrf_token = login_as_admin(client)

    response = client.post(
        '/api/rbac/roles',
        json={'name': 'editor', 'description': 'Editor role'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'Forbidden.'


def test_rbac_management_endpoints_success(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='rbac.manage',
        resource='rbac',
        action='manage',
    )
    csrf_token = login_as_admin(client)

    create_role_response = client.post(
        '/api/rbac/roles',
        json={'name': 'editor', 'description': 'Editor role'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_role_response.status_code == 201
    role_id = create_role_response.json()['id']

    create_permission_response = client.post(
        '/api/rbac/permissions',
        json={'name': 'news.publish', 'resource': 'news', 'action': 'publish'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_permission_response.status_code == 201
    permission_id = create_permission_response.json()['id']

    assign_permission_response = client.post(
        f'/api/rbac/roles/{role_id}/permissions/{permission_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert assign_permission_response.status_code == 200

    me_response = client.get('/api/auth/me')
    assert me_response.status_code == 200
    user_id = me_response.json()['user']['id']

    assign_role_response = client.post(
        f'/api/rbac/users/{user_id}/roles/{role_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert assign_role_response.status_code == 200

    my_permissions_response = client.get('/api/rbac/me/permissions')
    assert my_permissions_response.status_code == 200
    assert 'rbac.manage' in my_permissions_response.json()['permissions']
    assert 'news.publish' in my_permissions_response.json()['permissions']


def test_permission_registry_has_valid_unique_m09_permissions() -> None:
    permissions = get_registered_permissions()

    assert len(permissions) == len({permission.name for permission in permissions})
    assert {
        'signature.read',
        'signature.create',
        'signature.revoke',
        'signature.manage',
    } <= get_registered_permission_names()
    assert all(permission.name == f'{permission.resource}.{permission.action}' for permission in permissions)


def test_registry_managed_permission_cannot_be_deleted(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='rbac.manage',
        resource='rbac',
        action='manage',
    )
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='signature.manage',
        resource='signature',
        action='manage',
    )
    csrf_token = login_as_admin(client)

    permissions_response = client.get('/api/rbac/permissions/query?page=1&page_size=100')
    managed_permission = next(
        item
        for item in permissions_response.json()['items']
        if item['name'] == 'signature.manage'
    )

    response = client.delete(
        f"/api/rbac/permissions/{managed_permission['id']}",
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )

    assert response.status_code == 409


def test_replace_role_permissions_batch(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='rbac.manage',
        resource='rbac',
        action='manage',
    )
    csrf_token = login_as_admin(client)
    role_response = client.post(
        '/api/rbac/roles',
        json={'name': 'batch-role', 'description': 'Batch assignment'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    first_permission = client.post(
        '/api/rbac/permissions',
        json={'name': 'demo.read', 'resource': 'demo', 'action': 'read'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    ).json()
    second_permission = client.post(
        '/api/rbac/permissions',
        json={'name': 'demo.write', 'resource': 'demo', 'action': 'write'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    ).json()

    response = client.put(
        f"/api/rbac/roles/{role_response.json()['id']}/permissions",
        json={'permission_ids': [first_permission['id'], second_permission['id']]},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )

    assert response.status_code == 200
    assert response.json()['permissions'] == ['demo.read', 'demo.write']

    replace_response = client.put(
        f"/api/rbac/roles/{role_response.json()['id']}/permissions",
        json={'permission_ids': [second_permission['id'], 999999]},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert replace_response.status_code == 400
