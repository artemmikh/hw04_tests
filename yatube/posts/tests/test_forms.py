from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='group-slug',
            description='Тестовое описание группы',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'test text',
            'group': self.group.id,
        }
        # создаю пост
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.first()
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': new_post.author})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertEqual(form_data['text'], new_post.text)
        self.assertEqual(self.user, new_post.author)
        self.assertEqual(self.group, new_post.group)

    def test_edit_post(self):
        """Валидная форма измененяет пост в базе данных."""
        form_data = {
            'text': 'test text',
            'group': self.group.id
        }
        # создание поста
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # редактирование поста
        post = Post.objects.first()
        new_form_data = {
            'text': 'new test texst',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': post.id
                }
            ),
            data=new_form_data,
            follow=True,
        )
        modified_post = Post.objects.get(id=1)
        self.assertEqual(modified_post.text, new_form_data['text'])

    def test_guest_client_can_not_create_post(self):
        '''Неавторизованный пользователь не может опубликовать пост.'''
        form_data = {
            'text': 'test text',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        login_url = reverse('users:login')
        create_url = reverse('posts:post_create')
        self.assertRedirects(response, f'{login_url}?next={create_url}')
