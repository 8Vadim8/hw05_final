from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post
from .constant_list import (ANOTHER_USER, GROUP_DESCRIPTION, GROUP_SLUG,
                            GROUP_TITLE, NEW_POST_TEXT, NEW_USER, POST_TEXT,
                            USERNAME)

User = get_user_model()


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
            group=cls.group
        )
        cls.user = User.objects.create_user(username=ANOTHER_USER)
        cls.new_user = User.objects.create_user(username=NEW_USER)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_authorized_client = Client()

    def test_follow(self):
        """Проверка подписки и отписки от автора."""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            ),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1,
                         'Пользователь не подписался')
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            ),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), follow_count,
                         'Пользователь не отписался')

    def test_update(self):
        """
        Проверка, что новый пост появляется в ленте подписчика
        и не появляется в ленте неподписчика
        """
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            ),
            follow=True
        )
        # Смотрим страницу избранных авторов подписчика
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        # Проверяем, что у подписчика есть пост автора
        self.assertIsNotNone(list(response.context['page_obj']))
        # Смотрим страницу избранных авторов у неподписчика
        response = self.new_authorized_client.get(
            reverse('posts:follow_index')
        )
        # Проверяем, что у неподписчика нет постов
        self.assertIsNone(response.context)
        new_post = Post.objects.create(
            author=self.author,
            text=NEW_POST_TEXT,
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(new_post, list(response.context['page_obj']))
        response = self.new_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIsNone(response.context)
