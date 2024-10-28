from django import forms

from .models import Post, Comment, Group


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Замените 'your_group_id' на ID группы, которую хотите установить по умолчанию
            self.fields['group'].initial = Group.objects.get(id=4)
        except Group.DoesNotExist:
            # Если группа не найдена, можно оставить поле пустым
            self.fields['group'].initial = None


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
