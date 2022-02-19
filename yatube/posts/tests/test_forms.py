import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post
from .constant_list import (ANOTHER_USER, COMMENT, GROUP_DESCRIPTION,
                            GROUP_SLUG, GROUP_TITLE, NEW_POST_TEXT, POST_TEXT,
                            USERNAME)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.user = User.objects.create(username=USERNAME)

        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись."""
        posts_count = Post.objects.count()
        exist_posts_id = list(Post.objects.all().values_list('id', flat=True))
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': NEW_POST_TEXT,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        expected_post = Post.objects.filter(
            author=self.user
        ).exclude(id__in=exist_posts_id)[0]
        self.assertEqual(expected_post.text, form_data['text'])
        self.assertEqual(expected_post.group.id, form_data['group'])
        self.assertEqual(expected_post.image, 'posts/small.gif')

    def test_edit_post(self):
        """Валидная форма редактирует пост."""
        form_data = {
            'text': NEW_POST_TEXT,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(self.post.text, NEW_POST_TEXT)

    def test_anonymous_can_create_post(self):
        """Проверка на создание поста неавторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': NEW_POST_TEXT,
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.post.refresh_from_db()
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_anonymous_can_edit_post(self):
        """Проверка на изменение поста неавторизованным пользователем."""
        form_data = {
            'text': NEW_POST_TEXT,
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, POST_TEXT)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_non_author_can_edit_post(self):
        """Проверка на изменение поста не автором поста."""
        new_user = User.objects.create(username=ANOTHER_USER)
        another_authorized_client = Client()
        another_authorized_client.force_login(new_user)
        form_data = {
            'text': NEW_POST_TEXT,
        }
        response = another_authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, POST_TEXT)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_non_authorized_user_can_add_comment(self):
        """
        Проверка на добавление комментария неавторизованным пользователем.
        """
        count_comments = self.post.comments.count()
        form_data = {
            'text': COMMENT,
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.post.refresh_from_db()
        self.assertEqual(
            count_comments,
            self.post.comments.count()
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

    def test_authorized_user_can_add_comment(self):
        """Проверка добавления комментария авторизованным пользователем."""
        form_data = {
            'text': COMMENT,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, COMMENT)
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertIn(comment, response.context.get('comments'))
