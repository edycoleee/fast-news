from app.core.config import settings

VALID_SIGNATURE_DATA_URL = (
    'data:image/png;base64,'
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
)


def login_and_get_csrf(client, username_or_email='admin@example.com', password='StrongPass123!'):
    response = client.post(
        '/api/auth/login',
        json={'username_or_email': username_or_email, 'password': password},
    )
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def setup_signature_manager(create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='signature.manage',
        resource='signature',
        action='manage',
    )
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='file.manage',
        resource='file',
        action='manage',
    )


def create_signature(client, csrf_token, **overrides):
    payload = {
        'purpose': 'Approve editorial release',
        'news_id': None,
        'signature_data_url': VALID_SIGNATURE_DATA_URL,
    }
    payload.update(overrides)
    return client.post(
        '/api/signatures',
        json=payload,
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )


def test_signature_requires_create_permission(client, create_user) -> None:
    create_user()
    csrf_token = login_and_get_csrf(client)

    response = create_signature(client, csrf_token)

    assert response.status_code == 403


def test_signature_read_permission_cannot_create(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='signature.read',
        resource='signature',
        action='read',
    )
    csrf_token = login_and_get_csrf(client)

    list_response = client.get('/api/signatures/query?page=1&page_size=10')
    create_response = create_signature(client, csrf_token)

    assert list_response.status_code == 200
    assert create_response.status_code == 403


def test_signature_create_list_download_revoke(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_signature_manager(create_user, assign_permission_to_user)
    csrf_token = login_and_get_csrf(client)

    create_response = create_signature(client, csrf_token)
    assert create_response.status_code == 201
    signature = create_response.json()
    assert signature['status'] == 'active'
    assert signature['signer_id'] is not None

    list_response = client.get('/api/signatures/query?page=1&page_size=10')
    assert list_response.status_code == 200
    assert list_response.json()['total'] == 1

    detail_response = client.get(f"/api/signatures/{signature['id']}")
    assert detail_response.status_code == 200

    download_response = client.get(f"/api/signatures/{signature['id']}/download")
    assert download_response.status_code == 200
    assert download_response.headers['content-type'].startswith('image/png')

    public_download_response = client.get(f"/api/public/files/{signature['file_asset_id']}/download")
    assert public_download_response.status_code == 404

    delete_file_response = client.delete(
        f"/api/files/{signature['file_asset_id']}",
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert delete_file_response.status_code == 409

    revoke_response = client.post(
        f"/api/signatures/{signature['id']}/revoke",
        json={'reason': 'Approval request withdrawn'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert revoke_response.status_code == 200
    assert revoke_response.json()['status'] == 'revoked'
    assert revoke_response.json()['revoked_by_id'] == signature['signer_id']

    duplicate_revoke_response = client.post(
        f"/api/signatures/{signature['id']}/revoke",
        json={'reason': 'Duplicate attempt'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert duplicate_revoke_response.status_code == 409


def test_signature_rejects_invalid_png(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_signature_manager(create_user, assign_permission_to_user)
    csrf_token = login_and_get_csrf(client)

    response = create_signature(
        client,
        csrf_token,
        signature_data_url='data:image/png;base64,bm90LWEtcG5n',
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid PNG signature content.'


def test_signature_rejects_missing_news(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_signature_manager(create_user, assign_permission_to_user)
    csrf_token = login_and_get_csrf(client)

    response = create_signature(client, csrf_token, news_id=999999)

    assert response.status_code == 404
    assert response.json()['detail'] == 'News not found.'


def test_signature_requires_csrf(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_signature_manager(create_user, assign_permission_to_user)
    login_and_get_csrf(client)

    response = client.post(
        '/api/signatures',
        json={
            'purpose': 'Approve editorial release',
            'news_id': None,
            'signature_data_url': VALID_SIGNATURE_DATA_URL,
        },
    )

    assert response.status_code == 403
