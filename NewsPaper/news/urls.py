from django.urls import path
from .views import (
    NewsList, NewsDetail, news_search,
    NewsCreateView, NewsUpdateView, NewsDeleteView,
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView, add_comment
)

urlpatterns = [
    # Список и детали
    path('', NewsList.as_view(), name='news_list'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),

    # Поиск
    path('search/', news_search, name='news_search'),

    # Новости: создание, редактирование, удаление
    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

    # Статьи: создание, редактирование, удаление
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),

    path('<int:pk>/comment/', add_comment, name='add_comment'),
]