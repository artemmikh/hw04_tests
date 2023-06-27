from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='group-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[self.group.slug]): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[self.user]): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[self.post.id]): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html'
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.text, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        self.assertEqual(first_object, self.post)
        self.assertEqual(second_object, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        test_post = response.context['post_pk']
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
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
        response_index = self.authorized_client.get(reverse('posts:index'))
        post_in_index = response_index.context['page_obj'][0]
        self.assertEqual(post_in_index, self.post)
        self.assertEqual(post_in_index.group, self.post.group)

        response_group_list = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response_group_list.context['page_obj'][0]
        second_object = response_group_list.context['group']
        self.assertEqual(first_object, self.post)
        self.assertEqual(second_object, self.group)

        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        first_object = response_profile.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)


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

        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text=f'Пост {i}',
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        templates_page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user])
        ]
        for reverse_name in templates_page_names:
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        page = '?page=2'
        templates_page_names = [
            reverse('posts:index') + page,
            reverse('posts:group_list', args=[self.group.slug]) + page,
            reverse('posts:profile', args=[self.user]) + page
        ]
        for reverse_name in templates_page_names:
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), 3)
