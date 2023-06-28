from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем авторизованый клиент
        cls.user = User.objects.create_user(username='StasBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.GROUP_URL = f'/group/{cls.group.slug}/'
        cls.INDEX_URL = '/'
        cls.PROFILE_URL = f'/profile/{cls.user}/'
        cls.POST_DETAIL_URL = f'/posts/{cls.post.id}/'
        cls.POST_CREATE_URL = '/create/'
        cls.POST_EDIT_URL = f'/posts/{cls.post.id}/edit/'

        cls.guest_access = [
            cls.INDEX_URL,
            cls.GROUP_URL,
            cls.PROFILE_URL,
            cls.POST_DETAIL_URL,
        ]
        cls.authorized_access = [
            cls.POST_CREATE_URL,
            cls.POST_EDIT_URL,
        ]

    def test_guest_access_url_exists_at_desired_location(self):
        '''Проверяем общедоступные страницы.'''
        for i in self.guest_access:
            response = self.guest_client.get(i)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_access_url_exists_at_desired_location(self):
        '''Проверяем страницы доступные только авторизованному.'''
        for i in self.authorized_access:
            response = self.authorized_client.get(i)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_an_unauthorized_user(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(
            self.POST_CREATE_URL
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.INDEX_URL: 'posts/index.html',
            self.GROUP_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_CREATE_URL: 'posts/post_create.html',
            self.POST_EDIT_URL: 'posts/post_create.html'
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
