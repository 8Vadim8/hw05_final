from typing import Any

from django.core.paginator import Page, Paginator
from django.conf import settings


def get_paginator_page(request: Any, query_set: Any) -> Page:
    paginator = Paginator(query_set, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
