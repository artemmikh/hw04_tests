from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


from posts.models import Group, Post, Comment

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
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.image = SimpleUploadedFile(
            name='gifff',
            content=cls.gif,
            content_type='image/gif'
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
        modified_post = Post.objects.first()
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

    def test_guest_client_can_not_create_comment(self):
        '''Неавторизованный пользователь
        не может опубликовать комментарий.'''
        form_data = {
            'text': 'комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
        )
        login_url = reverse('users:login')
        create_url = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id})
        self.assertRedirects(response, f'{login_url}?next={create_url}')

    def test_create_comment(self):
        """После успешной отправки комментарий появляется
        на странице поста."""
        form_data = {
            'text': 'комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
        )
        self.assertEqual(form_data['text'], Comment.objects.first().text)
