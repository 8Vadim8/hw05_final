import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from .constant_list import (GROUP_TITLE, GROUP_SLUG, GROUP_DESCRIPTION,
                            USERNAME, POST_TEXT, NEW_POST_TEXT,
                            NEW_GROUP_TITLE, NEW_GROUP_SLUG,
                            NEW_GROUP_DESCRIPTION, NEW_GROUP_POST_TEXT)
from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            image=uploaded,
        )
        cls.post_counter = 1

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'{template} не соответствует'
                )

    def check_context(self, response, address, key):
        """Проверяем контекст в шаблонах."""
        if key != '4':
            post = response.context['page_obj'][0]
        else:
            post = response.context['post']
        post_text = post.text
        post_group = post.group.title
        post_author = post.author.username
        post_image = post.image
        self.assertEqual(
            post.id,
            self.post.id,
            f'В шаблоне {address} id поста не совпадает'
        )
        self.assertEqual(
            post_text,
            POST_TEXT,
            (f'В шаблоне {address} текст поста'
             ' не соответствует контексту')
        )
        self.assertEqual(
            post_group,
            GROUP_TITLE,
            (f'В шаблоне {address} название группы'
             ' не соответствует контексту')
        )
        self.assertEqual(
            post_author,
            USERNAME,
            f'В шаблоне {address} автор поста указан не верно'
        )
        if post_image is not None:
            self.assertEqual(
                post_image,
                self.post.image,
                f'В шаблоне {address} картинка поста не соответствует'
            )
        if key == '2':
            group_description = post.group.description
            self.assertEqual(
                group_description,
                GROUP_DESCRIPTION,
                f'В шаблоне {address} описание группы не верно'
            )
        elif key == '3':
            counter = len(response.context['page_obj'])
            self.assertEqual(
                counter,
                self.post_counter,
                (f'В шаблоне {address} количество постов указано'
                 ' не верно')
            )
        elif key == '4':
            self.assertEqual(
                response.context['count'],
                self.post_counter,
                (f'В шаблоне {address} количество постов указано'
                 ' не верно')
            )

    def test_index_group_profile_show_correct_context(self):
        """
        Шаблон index, group_post, profile сформирован с правильным контекстом.
        """
        address_list = {
            '1': reverse('posts:index'),
            '2': reverse('posts:group_posts',
                         kwargs={'slug': self.group.slug}),
            '3': reverse('posts:profile',
                         kwargs={'username': self.user}),
            '4': reverse('posts:post_detail',
                         kwargs={'post_id': self.post.id})
        }
        for key, address in address_list.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.check_context(response, address, key)

    def test_post_create_and_edit_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контесктом."""
        links = [reverse('posts:post_create'),
                 reverse('posts:post_edit', kwargs={'post_id': self.post.id})]
        for link in links:
            response = self.authorized_client.get(link)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_additional_testing_by_create_new_post(self):
        """
        Дополнительная проверка при создании поста, что он появляется
        на главной странице, странице пользователя и странице группы
        """
        new_group = Group.objects.create(
            title=NEW_GROUP_TITLE,
            slug=NEW_GROUP_SLUG,
            description=NEW_GROUP_DESCRIPTION,
        )
        new_group_post = Post.objects.create(
            author=PostViewTests.user,
            text=NEW_GROUP_POST_TEXT,
            group=new_group,
        )
        exist_posts_id = list(Post.objects.all().values_list('id', flat=True))
        new_post = Post.objects.create(
            author=PostViewTests.user,
            text=NEW_POST_TEXT,
            group=PostViewTests.group,
        )
        links = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        ]
        for link in links:
            response = self.authorized_client.get(link)
            expected_post = Post.objects.filter(author=self.user).exclude(
                id__in=exist_posts_id)
            self.assertIn(expected_post[0],
                          response.context['page_obj'])
            post_text = expected_post[0].text
            post_group = expected_post[0].group.title
            self.assertEqual(post_text, new_post.text,
                             f'текст не соответствует в {link}')
            self.assertEqual(post_group, new_post.group.title,
                             f'группа не соответсвует в {link}')

        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': new_group.slug})
        )
        self.assertNotIn(expected_post[0],
                         response.context['page_obj'])
        self.assertIn(Post.objects.get(id=new_group_post.id),
                      response.context['page_obj'])

    def test_cache_index_page_correct_context(self):
        """Кэш index сформирован с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        content_with_post = response.content
        post_delete = Post.objects.get(pk=self.post.id)
        post_delete.delete()
        response = self.client.get(reverse('posts:index'))
        cache_content = response.content
        self.assertEqual(content_with_post, cache_content)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        clear_cache_content = response.content
        self.assertNotEqual(content_with_post, clear_cache_content)
