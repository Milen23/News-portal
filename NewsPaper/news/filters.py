import django_filters
from django_filters import DateFilter, CharFilter
from .models import Post
from django.contrib.auth.models import User
from django import forms


class NewsFilter(django_filters.FilterSet):
    # Фильтр по названию (содержит слово)
    title = CharFilter(field_name='title', lookup_expr='icontains', label='Название содержит')

    # Фильтр по имени автора (через связь с User)
    author = CharFilter(field_name='author__user__username', lookup_expr='icontains', label='Имя автора содержит')

    # Фильтр по дате (позже указанной даты)
    date_after = DateFilter(field_name='created_at', lookup_expr='gte', label='Дата позже',
                            widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Post
        fields = ['title', 'author', 'date_after']