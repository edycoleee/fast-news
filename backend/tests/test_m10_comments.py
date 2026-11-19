from app.core.config import settings


def login_and_get_csrf(client, username_or_email='admin@example.com', password='StrongPass123!'):
    response = client.post(
        '/api/auth/login',
        json={'username_or_email': username_or_email, 'password': password},
    )
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def setup_comment_admin(
    create_user,
    assign_permission_to_user,
    *,
    permissions=('comment.read', 'comment.moderate', 'comment.delete'),
) -> None:
    create_user()
    for name in permissions:
        assign_permission_to_user(
            user_email='admin@example.com',
            permission_name=name,
            resource='comment',
            action=name.split('.')[1],
        )


def create_published_news(client, csrf_token) -> str:
    response = client.post(
        '/api/news',
        json={
            'title': 'Published comment target',
            'slug': 'published-comment-target',
            'summary': 'Comment workflow test',
            'content': '<p>Published article content.</p>',
            'status': 'published',
            'category_id': None,
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert response.status_code == 201
    return response.json()['slug']


def test_public_comment_pending_is_hidden_then_can_be_approved(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_comment_admin(create_user, assign_permission_to_user)
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)
    slug = create_published_news(client, csrf_token)

    submit_response = client.post(
        f'/api/public/news/{slug}/comments',
        json={
            'author_name': 'Pembaca',
            'content': '<b>Konten komentar</b>',
            'parent_id': None,
        },
    )
    assert submit_response.status_code == 201
    comment_id = submit_response.json()['id']

    public_before_response = client.get(f'/api/public/news/{slug}/comments')
    assert public_before_response.status_code == 200
    assert public_before_response.json() == []

    admin_list_response = client.get('/api/comments/query?status_filter=pending')
    assert admin_list_response.status_code == 200
    assert admin_list_response.json()['total'] == 1
    assert admin_list_response.json()['items'][0]['content'] == 'Konten komentar'

    approve_response = client.post(
        f'/api/comments/{comment_id}/moderate',
        json={'status': 'approved', 'note': 'Sesuai kebijakan'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()['status'] == 'approved'

    public_after_response = client.get(f'/api/public/news/{slug}/comments')
    assert public_after_response.status_code == 200
    assert len(public_after_response.json()) == 1
    assert public_after_response.json()[0]['author_name'] == 'Pembaca'
    assert public_after_response.json()[0]['content'] == 'Konten komentar'

    duplicate_response = client.post(
        f'/api/comments/{comment_id}/moderate',
        json={'status': 'rejected', 'note': 'Duplicate'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert duplicate_response.status_code == 409


def test_comment_permissions_are_granular(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)
    slug = create_published_news(client, csrf_token)
    submit_response = client.post(
        f'/api/public/news/{slug}/comments',
        json={'author_name': 'Reader', 'content': 'A useful comment', 'parent_id': None},
    )
    comment_id = submit_response.json()['id']
    client.post(
        '/api/auth/logout',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )

    create_user(
        username='reader-moderator',
        email='reader-moderator@example.com',
    )
    assign_permission_to_user(
        user_email='reader-moderator@example.com',
        permission_name='comment.read',
        resource='comment',
        action='read',
    )
    reader_csrf_token = login_and_get_csrf(
        client,
        username_or_email='reader-moderator@example.com',
    )

    moderate_response = client.post(
        f'/api/comments/{comment_id}/moderate',
        json={'status': 'approved', 'note': None},
        headers={settings.CSRF_HEADER_NAME: reader_csrf_token},
    )

    assert moderate_response.status_code == 403


def test_comment_moderation_requires_csrf(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_comment_admin(create_user, assign_permission_to_user)
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)
    slug = create_published_news(client, csrf_token)
    submit_response = client.post(
        f'/api/public/news/{slug}/comments',
        json={'author_name': 'Reader', 'content': 'Pending comment', 'parent_id': None},
    )

    response = client.post(
        f"/api/comments/{submit_response.json()['id']}/moderate",
        json={'status': 'approved', 'note': None},
    )

    assert response.status_code == 403


def test_comment_reject_delete_and_invalid_parent(
    client,
    create_user,
    assign_permission_to_user,
) -> None:
    setup_comment_admin(create_user, assign_permission_to_user)
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)
    slug = create_published_news(client, csrf_token)

    invalid_parent_response = client.post(
        f'/api/public/news/{slug}/comments',
        json={'author_name': 'Reader', 'content': 'Nested comment', 'parent_id': 999},
    )
    assert invalid_parent_response.status_code == 400

    submit_response = client.post(
        f'/api/public/news/{slug}/comments',
        json={'author_name': 'Reader', 'content': 'Reject this comment', 'parent_id': None},
    )
    comment_id = submit_response.json()['id']

    reject_response = client.post(
        f'/api/comments/{comment_id}/moderate',
        json={'status': 'rejected', 'note': 'Off topic'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert reject_response.status_code == 200
    assert reject_response.json()['status'] == 'rejected'

    delete_response = client.delete(
        f'/api/comments/{comment_id}',
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert delete_response.status_code == 200

    public_response = client.get(f'/api/public/news/{slug}/comments')
    assert public_response.json() == []


def test_public_comment_rejects_invalid_news_and_content(
    client,
) -> None:
    missing_news_response = client.post(
        '/api/public/news/missing-news/comments',
        json={'author_name': 'Reader', 'content': 'A valid comment', 'parent_id': None},
    )
    assert missing_news_response.status_code == 404

    invalid_content_response = client.post(
        '/api/public/news/missing-news/comments',
        json={'author_name': 'R', 'content': 'x', 'parent_id': None},
    )
    assert invalid_content_response.status_code == 422
