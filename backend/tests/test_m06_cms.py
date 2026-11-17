from app.core.config import settings


def login_and_get_csrf(client, username_or_email='admin@example.com', password='StrongPass123!'):
    response = client.post(
        '/api/auth/login',
        json={'username_or_email': username_or_email, 'password': password},
    )
    assert response.status_code == 200
    return client.cookies.get(settings.CSRF_COOKIE_NAME)


def test_category_news_forbidden_without_permissions(client, create_user) -> None:
    create_user()
    csrf_token = login_and_get_csrf(client)

    category_response = client.post(
        '/api/categories',
        json={'name': 'Technology', 'slug': 'technology'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert category_response.status_code == 403

    news_response = client.post(
        '/api/news',
        json={
            'title': 'News One',
            'slug': 'news-one',
            'summary': 'Summary',
            'content': 'Content body',
            'status': 'draft',
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert news_response.status_code == 403


def test_category_and_news_crud_success(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='category.manage',
        resource='category',
        action='manage',
    )
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    create_category_response = client.post(
        '/api/categories',
        json={'name': 'Technology', 'slug': 'technology', 'description': 'Tech updates'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_category_response.status_code == 201
    category_id = create_category_response.json()['id']

    list_categories_response = client.get('/api/categories')
    assert list_categories_response.status_code == 200
    assert len(list_categories_response.json()) == 1

    paged_categories_response = client.get('/api/categories/query?page=1&page_size=1&search=tech')
    assert paged_categories_response.status_code == 200
    assert paged_categories_response.json()['total'] == 1
    assert len(paged_categories_response.json()['items']) == 1

    create_news_response = client.post(
        '/api/news',
        json={
            'title': 'First Post',
            'slug': 'first-post',
            'summary': 'Summary',
            'content': 'Content body',
            'status': 'draft',
            'category_id': category_id,
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_news_response.status_code == 201
    news_id = create_news_response.json()['id']

    public_news_before_publish = client.get('/api/public/news')
    assert public_news_before_publish.status_code == 200
    assert public_news_before_publish.json() == []

    update_news_response = client.put(
        f'/api/news/{news_id}',
        json={'status': 'published'},
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert update_news_response.status_code == 200
    assert update_news_response.json()['status'] == 'published'

    public_news_after_publish = client.get('/api/public/news')
    assert public_news_after_publish.status_code == 200
    assert len(public_news_after_publish.json()) == 1
    assert public_news_after_publish.json()[0]['slug'] == 'first-post'

    public_news_detail = client.get('/api/public/news/first-post')
    assert public_news_detail.status_code == 200
    assert public_news_detail.json()['title'] == 'First Post'

    paged_news_response = client.get('/api/news/query?page=1&page_size=1&status_filter=published')
    assert paged_news_response.status_code == 200
    assert paged_news_response.json()['total'] == 1
    assert len(paged_news_response.json()['items']) == 1


def test_news_manager_can_read_category_options(client, create_user, assign_permission_to_user) -> None:
    create_user()
    create_user(username='editor', email='editor@example.com', password='StrongPass123!')

    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='category.manage',
        resource='category',
        action='manage',
    )
    admin_csrf = login_and_get_csrf(client)
    create_category_response = client.post(
        '/api/categories',
        json={'name': 'Business', 'slug': 'business'},
        headers={settings.CSRF_HEADER_NAME: admin_csrf},
    )
    assert create_category_response.status_code == 201

    client.post(
        '/api/auth/logout',
        headers={settings.CSRF_HEADER_NAME: client.cookies.get(settings.CSRF_COOKIE_NAME)},
    )

    assign_permission_to_user(
        user_email='editor@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    login_and_get_csrf(client, username_or_email='editor@example.com')

    categories_query_response = client.get('/api/categories/query?page=1&page_size=10')
    assert categories_query_response.status_code == 200
    assert categories_query_response.json()['total'] == 1


def test_news_content_is_sanitized_before_publish(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    create_news_response = client.post(
        '/api/news',
        json={
            'title': 'Sanitized Post',
            'slug': 'sanitized-post',
            'summary': 'Summary',
            'content': '<p>Hello</p><script>alert(1)</script><a href="javascript:alert(1)">Click</a>',
            'status': 'published',
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_news_response.status_code == 201
    assert '<script>' not in create_news_response.json()['content']
    assert 'javascript:alert' not in create_news_response.json()['content']

    public_news_detail = client.get('/api/public/news/sanitized-post')
    assert public_news_detail.status_code == 200
    assert '<script>' not in public_news_detail.json()['content']


def test_news_image_tag_is_allowed_after_sanitization(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    create_news_response = client.post(
        '/api/news',
        json={
            'title': 'Image Post',
            'slug': 'image-post',
            'summary': 'Summary',
            'content': '<p>Image:</p><img src="https://example.com/a.png" alt="img">',
            'status': 'published',
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_news_response.status_code == 201
    assert '<img' in create_news_response.json()['content']


def test_markdown_image_is_converted_for_public_detail(client, create_user, assign_permission_to_user) -> None:
    create_user()
    assign_permission_to_user(
        user_email='admin@example.com',
        permission_name='news.manage',
        resource='news',
        action='manage',
    )
    csrf_token = login_and_get_csrf(client)

    create_news_response = client.post(
        '/api/news',
        json={
            'title': 'Markdown Image Post',
            'slug': 'markdown-image-post',
            'summary': 'Summary',
            'content': '![preview](https://example.com/image.png)',
            'status': 'published',
        },
        headers={settings.CSRF_HEADER_NAME: csrf_token},
    )
    assert create_news_response.status_code == 201

    public_news_detail = client.get('/api/public/news/markdown-image-post')
    assert public_news_detail.status_code == 200
    assert '<img' in public_news_detail.json()['content']
