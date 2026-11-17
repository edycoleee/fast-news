from app.core.config import settings


def login_and_get_csrf(client, username_or_email='admin@example.com', password='StrongPass123!'):
    response = client.post(
        '/api/auth/login',
        json={'username_or_email': username_or_email, 'password': password},
    )
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def test_users_and_rbac_crud_baseline(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='rbac.manage',
        resource='rbac',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    create_user_response = client.post(
        '/api/users',
        json={
            'username': 'editor',
            'email': 'editor@example.com',
            'password': 'StrongPass123!',
            'is_active': True,
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_user_response.status_code == 201
    user_id = create_user_response.json()['id']

    list_users_response = client.get('/api/users/query?page=1&page_size=10')
    assert list_users_response.status_code == 200
    assert list_users_response.json()['total'] >= 2

    create_role_response = client.post(
        '/api/rbac/roles',
        json={'name': 'editor-role', 'description': 'Editor role'},
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

    list_roles_response = client.get('/api/rbac/roles/query?page=1&page_size=10')
    assert list_roles_response.status_code == 200
    assert list_roles_response.json()['total'] >= 1

    list_permissions_response = client.get('/api/rbac/permissions/query?page=1&page_size=10')
    assert list_permissions_response.status_code == 200
    assert list_permissions_response.json()['total'] >= 1

    assign_permission_response = client.post(
        f'/api/rbac/roles/{role_id}/permissions/{permission_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert assign_permission_response.status_code == 200

    role_permissions_response = client.get(f'/api/rbac/roles/{role_id}/permissions')
    assert role_permissions_response.status_code == 200
    assert 'news.publish' in role_permissions_response.json()['permissions']

    assign_role_response = client.post(
        f'/api/rbac/users/{user_id}/roles/{role_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert assign_role_response.status_code == 200

    user_roles_response = client.get(f'/api/rbac/users/{user_id}/roles')
    assert user_roles_response.status_code == 200
    assert 'editor-role' in user_roles_response.json()['roles']

    user_permissions_response = client.get(f'/api/rbac/users/{user_id}/permissions')
    assert user_permissions_response.status_code == 200
    assert 'news.publish' in user_permissions_response.json()['permissions']
