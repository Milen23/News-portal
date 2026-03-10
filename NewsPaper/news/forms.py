from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']  # Убедись, что categories есть в fields
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст', 'rows': 10}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),  # SelectMultiple для выбора нескольких категорий
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Текст',
            'categories': 'Категории',
        }