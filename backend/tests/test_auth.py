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
