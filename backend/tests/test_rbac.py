from app.core.config import settings


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
