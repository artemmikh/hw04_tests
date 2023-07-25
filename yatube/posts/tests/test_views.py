from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()
POSTS_PER_PAGE = settings.POSTS_PER_PAGE


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='название группы',
            slug='test-slug',
            description='Описание группы',
        )
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group,
            image=cls.image,
        )
        cls.GROUP_REVERSE = reverse('posts:group_list', args=[cls.group.slug])
        cls.INDEX_REVERSE = reverse('posts:index')
        cls.PROFILE_REVERSE = reverse('posts:profile', args=[cls.user])
        cls.POST_DETAIL_REVERSE = reverse(
            'posts:post_detail', args=[cls.post.id]
        )
        cls.POST_CREATE_REVERSE = reverse('posts:post_create')
        cls.POST_EDIT_REVERSE = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            self.INDEX_REVERSE: 'posts/index.html',
            self.GROUP_REVERSE: 'posts/group_list.html',
            self.PROFILE_REVERSE: 'posts/profile.html',
            self.POST_DETAIL_REVERSE: 'posts/post_detail.html',
            self.POST_CREATE_REVERSE: 'posts/post_create.html',
            self.POST_EDIT_REVERSE: 'posts/post_create.html'
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.guest_client.get(self.INDEX_REVERSE)
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.guest_client.get(
            self.GROUP_REVERSE
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        self.assertEqual(first_object, self.post)
        self.assertEqual(second_object, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.PROFILE_REVERSE)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(self.POST_DETAIL_REVERSE)
        test_post = response.context['post']
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_CREATE_REVERSE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_EDIT_REVERSE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_correct_create(self):
        """Если при создании поста указать группу, то этот пост появляется
        на главной странице сайта,
        на странице выбранной группы,
        в профайле пользователя."""
        response_index = self.authorized_client.get(self.INDEX_REVERSE)
        post_in_index = response_index.context['page_obj'][0]
        self.assertEqual(post_in_index, self.post)
        self.assertEqual(post_in_index.group, self.post.group)

        response_group_list = self.authorized_client.get(
            self.GROUP_REVERSE
        )
        first_object = response_group_list.context['page_obj'][0]
        second_object = response_group_list.context['group']
        self.assertEqual(first_object, self.post)
        self.assertEqual(second_object, self.group)

        response_profile = self.authorized_client.get(
            self.PROFILE_REVERSE)
        first_object = response_profile.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)

    def test_index_page_cache(self):
        """Данные главной страницы остаются в кеше."""
        post = Post.objects.create(
            text='test cache',
            author=self.user
        )
        response_index = self.guest_client.get(self.INDEX_REVERSE).content
        post.delete()
        cache_index = self.guest_client.get(self.INDEX_REVERSE).content
        self.assertEqual(response_index, cache_index)
        cache.clear()
        self.assertIsNot(response_index, cache_index)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы',
        )

        posts = [
            Post(author=cls.user,
                 text=f'Пост {i}',
                 group=cls.group) for i in range(13)
        ]
        Post.objects.bulk_create(posts)
        cls.GROUP_REVERSE = reverse('posts:group_list', args=[cls.group.slug])
        cls.INDEX_REVERSE = reverse('posts:index')
        cls.PROFILE_REVERSE = reverse('posts:profile', args=[cls.user])

    def test_first_page_contains_ten_records(self):
        templates_page_names = [
            self.INDEX_REVERSE,
            self.GROUP_REVERSE,
            self.PROFILE_REVERSE,
        ]
        for reverse_name in templates_page_names:
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        page = '?page=2'
        templates_page_names = [
            self.INDEX_REVERSE + page,
            self.GROUP_REVERSE + page,
            self.PROFILE_REVERSE + page,
        ]
        for reverse_name in templates_page_names:
            response = self.client.get(reverse_name)
            self.assertEqual(
                len(response.context['page_obj']),
                Post.objects.count() % POSTS_PER_PAGE
            )
