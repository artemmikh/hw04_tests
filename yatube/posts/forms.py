from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        # На основе какой модели создаётся класс формы
        model = Post
        # Укажем, какие поля будут в форме
        fields = ('text', 'group',)
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        empty_label = {
            'group': 'Пост без группы',
        }
