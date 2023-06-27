from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
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

    # Проверяем общедоступные страницы
    def test_home_url_exists_at_desired_location(self):
        """Страница index доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.status_code, 200)

    def test_group_page_is_available_to_any_user(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_username_page_is_available_to_any_user(self):
        """Страница /profile/<username>/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user})

        )
        self.assertEqual(response.status_code, 200)

    def test_post_id_page_is_available_to_any_user(self):
        """Страница /posts/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_page_is_available_to_an_authorized_user(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertEqual(response.status_code, 200)

    # Проверяем доступность изменения страниц для автора
    def test_changing_the_post_is_only_available_to_the_author(self):
        """Страница /posts/<post_id>/edit/
        доступна автору поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_redirect_for_an_unauthorized_user(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:post_create')
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
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

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
