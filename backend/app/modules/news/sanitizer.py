from __future__ import annotations

import re

import bleach

ALLOWED_TAGS = [
    'p',
    'br',
    'strong',
    'em',
    'u',
    's',
    'blockquote',
    'ul',
    'ol',
    'li',
    'h1',
    'h2',
    'h3',
    'a',
    'img',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def _convert_markdown_to_html(value: str) -> str:
    image_pattern = re.compile(r'!\[([^\]]*)\]\((https?://[^\s)]+)\)')
    link_pattern = re.compile(r'(?<!!)\[([^\]]+)\]\((https?://[^\s)]+)\)')

    converted = image_pattern.sub(r'<img src="\2" alt="\1" title="\1">', value)
    converted = link_pattern.sub(r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', converted)
    return converted


def sanitize_news_html(value: str) -> str:
    normalized_value = _convert_markdown_to_html(value)
    return bleach.clean(
        normalized_value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def has_meaningful_text(value: str) -> bool:
    if '<img' in value:
        return True
    plain_text = bleach.clean(value, tags=[], strip=True)
    normalized_text = re.sub(r'\s+', '', plain_text)
    return len(normalized_text) > 0
