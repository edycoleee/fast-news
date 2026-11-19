from app.core.config import settings


def test_login_me_and_logout_success(client, create_user) -> None:
    create_user()

    login_response = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )
    assert login_response.status_code == 200
    assert login_response.json()['user']['email'] == 'admin@example.com'
    assert settings.SESSION_COOKIE_NAME in login_response.cookies
    assert settings.CSRF_COOKIE_NAME in login_response.cookies

    me_response = client.get('/api/auth/me')
    assert me_response.status_code == 200
    assert me_response.json()['user']['username'] == 'admin'

    csrf_token = client.cookies.get(settings.CSRF_COOKIE_NAME)
    logout_response = client.post(
        '/api/auth/logout',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()['message'] == 'Logout successful.'

    me_after_logout_response = client.get('/api/auth/me')
    assert me_after_logout_response.status_code == 401


def test_login_rejects_invalid_password(client, create_user) -> None:
    create_user()

    response = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'WrongPass123!'},
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials.'


def test_logout_requires_csrf_header(client, create_user) -> None:
    create_user()

    login_response = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )
    assert login_response.status_code == 200

    logout_response = client.post('/api/auth/logout')
    assert logout_response.status_code == 403
    assert logout_response.json()['detail'] == 'CSRF token missing.'


def test_list_and_revoke_other_sessions(client, create_user) -> None:
    create_user()
    first_login = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )
    assert first_login.status_code == 200
    first_csrf = client.cookies.get(settings.CSRF_COOKIE_NAME)

    second_client = __import__('fastapi.testclient', fromlist=['TestClient']).TestClient(client.app)
    second_login = second_client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    )
    assert second_login.status_code == 200

    sessions_response = client.get('/api/auth/sessions')
    assert sessions_response.status_code == 200
    assert len(sessions_response.json()['items']) == 2

    revoke_response = client.delete(
        '/api/auth/sessions',
        headers={settings.CSRF_HEADER_NAME: first_csrf},
    )
    assert revoke_response.status_code == 200
    assert revoke_response.json()['message'] == '1 session(s) revoked.'

    assert client.get('/api/auth/me').status_code == 200
    assert second_client.get('/api/auth/me').status_code == 401


def test_session_management_permission_for_all_sessions(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='session.manage',
        resource='session',
        action='manage',
    )
    csrf_token = client.post(
        '/api/auth/login',
        json={'username_or_email': 'admin@example.com', 'password': 'StrongPass123!'},
    ).cookies.get(settings.CSRF_COOKIE_NAME)

    assert client.get('/api/auth/sessions/all').status_code == 200
    session_id = client.get('/api/auth/sessions/all').json()['items'][0]['id']
    response = client.delete(
        f'/api/auth/sessions/{session_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert response.status_code == 200
    assert client.get('/api/auth/me').status_code == 401
