from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .constant_list import (GROUP_TITLE, GROUP_SLUG, GROUP_DESCRIPTION,
                            USERNAME, POST_TEXT, ANOTHER_USER)
from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group
        )
        cls.another_user = User.objects.create_user(username=ANOTHER_USER)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        url_exists_location = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            # '/unexisting_page/': HTTPStatus.OK,
        }
        for address, status in url_exists_location.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(
                    response.status_code,
                    status,
                    f'Страница {address} не доступна по этому адресу'
                )

    def test_post_create_exists_at_desired_location(self):
        """Страница Create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_exists_at_desired_location(self):
        """Страница Post edit доступна автору поста."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        """URL-адрес использует правильный шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Страница {address} использует неправильный шаблон'
                )

    def test_redirect_non_author(self):
        """Проверка redirect, если пользователь хочет изменить чужой пост."""
        response = self.another_authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_found(self):
        """test."""
        response = self.client.get(reverse('posts:index'))
        print(response.status_code)
        response = self.client.get('/tets/')
        self.assertEqual(
            response.status_code,
            404,
            'Страница unexisting_page/ не доступна по этому адресу'
        )
