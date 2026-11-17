from app.core.config import settings


def login_and_get_csrf(client, username_or_email='admin@example.com', password='StrongPass123!'):
    response = client.post(
        '/api/auth/login',
        json={'username_or_email': username_or_email, 'password': password},
    )
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def test_file_upload_forbidden_without_permissions(client, create_user) -> None:
    create_user()
    csrf_token = login_and_get_csrf(client)

    response = client.post(
        '/api/files/upload',
        files={'upload_file': ('sample.pdf', b'%PDF-1.4\nsample\n', 'application/pdf')},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert response.status_code == 403


def test_file_upload_list_download_delete_success(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    upload_response = client.post(
        '/api/files/upload',
        files={'upload_file': ('policy.pdf', b'%PDF-1.4\nsample\n', 'application/pdf')},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert upload_response.status_code == 201
    file_id = upload_response.json()['id']

    list_response = client.get('/api/files/query?page=1&page_size=10')
    assert list_response.status_code == 200
    assert list_response.json()['total'] == 1

    download_response = client.get(f'/api/files/{file_id}/download')
    assert download_response.status_code == 200
    assert download_response.headers['content-type'].startswith('application/pdf')

    delete_response = client.delete(
        f'/api/files/{file_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert delete_response.status_code == 200


def test_file_upload_rejects_invalid_pdf_content(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    upload_response = client.post(
        '/api/files/upload',
        files={'upload_file': ('bad.pdf', b'not-a-real-pdf', 'application/pdf')},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert upload_response.status_code == 400
