from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        # На основе какой модели создаётся класс формы
        model = Post
        # Укажем, какие поля будут в форме
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        empty_label = {
            'group': 'Пост без группы',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Текст комментария',
        }
