from django.contrib.auth import get_user_model

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .constant_list import (GROUP_TITLE, GROUP_SLUG, GROUP_DESCRIPTION,
                            USERNAME)
from ..models import Group, Post

User = get_user_model()
posts_list = []
NUMBER_OF_POSTS = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        for i in range(NUMBER_OF_POSTS):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )
            posts_list.append(cls.post)

    def test_1st_page_contains_10_records(self):
        """Проверка работы паджинатора на первой странице"""
        links = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for link in links:
            with self.subTest():
                response = self.client.get(link)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_PER_PAGE
                )

    def test_2nd_page_contains_3_records(self):
        """Проверка работы паджинатора на второй странице"""
        links = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for link in links:
            with self.subTest():
                response = self.client.get(link + '?page=2')
                number_of_posts = len(response.context['page_obj'])
                remaining_posts = NUMBER_OF_POSTS - settings.POSTS_PER_PAGE
                if remaining_posts >= 10:
                    self.assertEqual(number_of_posts,
                                     settings.POSTS_PER_PAGE)
                else:
                    self.assertEqual(
                        number_of_posts,
                        (remaining_posts % settings.POSTS_PER_PAGE)
                    )
