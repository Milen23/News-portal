from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from .models import Post, Author
from .filters import NewsFilter
from .forms import PostForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Category
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from .tasks import send_notification_to_subscribers, send_welcome_email




class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Добавляем информацию о подписке для каждой категории
        for category in context['categories']:
            category.user_is_subscribed = user in category.subscribers.all() if user.is_authenticated else False

        return context


@login_required
def subscribe_to_category(request, category_id):
    """Подписка пользователя на категорию"""
    user = request.user
    category = get_object_or_404(Category, id=category_id)

    # Проверяем, есть ли уже пользователь в подписчиках
    if user in category.subscribers.all():
        messages.warning(request, f'Вы уже подписаны на категорию "{category.name}"')
    else:
        category.subscribers.add(user)
        messages.success(request, f'Вы успешно подписались на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))

@login_required
def unsubscribe_from_category(request, category_id):
    """Отписка пользователя от категории"""
    user = request.user
    category = get_object_or_404(Category, id=category_id)

    if user in category.subscribers.all():
        category.subscribers.remove(user)
        messages.success(request, f'Вы отписались от категории "{category.name}"')
    else:
        messages.warning(request, f'Вы не были подписаны на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


def get_categories_with_subscription_status(user):
    """Возвращает все категории с информацией о подписке пользователя"""
    categories = Category.objects.all()
    for category in categories:
        category.user_is_subscribed = user in category.subscribers.all() if user.is_authenticated else False
    return categories

@login_required
def become_author(request):
    """Добавляет пользователя в группу authors"""
    user = request.user

    # Проверяем, не является ли пользователь уже автором
    authors_group = Group.objects.get(name='authors')

    if authors_group in user.groups.all():
        messages.warning(request, 'Вы уже являетесь автором!')
    else:
        user.groups.add(authors_group)
        messages.success(request, 'Поздравляем! Теперь вы автор и можете создавать статьи и новости.')

    return redirect('news_list')


class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'account/signup.html'
    success_url = reverse_lazy('account_login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        # Добавляем в группу common
        common_group = Group.objects.get(name='common')
        user.groups.add(common_group)

        # Асинхронная отправка приветственного письма
        send_welcome_email.delay(user.id)

        messages.success(self.request, 'Регистрация прошла успешно! Проверьте email для подтверждения.')
        return response


def add_comment(request, pk):
    if request.method == 'POST' and request.user.is_authenticated:
        post = Post.objects.get(pk=pk)
        text = request.POST.get('text')
        if text:
            Comment.objects.create(
                post=post,
                user=request.user,
                text=text,
                rating=0
            )
    return redirect('news_detail', pk=pk)

class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    context_object_name = 'news'
    queryset = Post.objects.filter(post_type='NW').order_by('-created_at')
    paginate_by = 10


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news'
    queryset = Post.objects.filter(post_type='NW')


# Поиск новостей
def news_search(request):
    news = Post.objects.filter(post_type='NW').order_by('-created_at')
    f = NewsFilter(request.GET, queryset=news)
    return render(request, 'news_search.html', {'filter': f})


# создание новости
class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def form_valid(self, form):
        author, created = Author.objects.get_or_create(user=self.request.user)

        # Проверяем лимит на 3 новости в сутки
        one_day_ago = timezone.now() - timedelta(days=1)
        news_count_today = Post.objects.filter(
            author=author,
            post_type='NW',
            created_at__gte=one_day_ago
        ).count()

        if news_count_today >= 3:
            messages.error(self.request, 'Вы не можете публиковать более 3 новостей в сутки!')
            return redirect('news_list')

        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author = author
        response = super().form_valid(form)

        # Асинхронная отправка уведомлений подписчикам
        send_notification_to_subscribers.delay(post.id)

        return response

    def handle_no_permission(self):
        messages.warning(self.request, 'У вас нет прав на создание новостей. Только авторы могут это делать!')
        return redirect('news_list')

# редактировать новость
class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'  # Требуется право на изменение

    def handle_no_permission(self):
        messages.warning(self.request, 'У вас нет прав на редактирование новостей.')
        return redirect('news_list')

    def get_queryset(self):
        # Пользователь может редактировать только свои новости
        return Post.objects.filter(post_type='NW', author__user=self.request.user)


# удаление новости
class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'  # Требуется право на удаление

    def handle_no_permission(self):
        messages.warning(self.request, 'У вас нет прав на удаление новостей.')
        return redirect('news_list')

    def get_queryset(self):
        # Пользователь может удалять только свои новости
        return Post.objects.filter(post_type='NW', author__user=self.request.user)


# создание статьи
class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def form_valid(self, form):
        author, created = Author.objects.get_or_create(user=self.request.user)

        # Проверяем лимит на 3 статьи в сутки
        one_day_ago = timezone.now() - timedelta(days=1)
        articles_count_today = Post.objects.filter(
            author=author,
            post_type='AR',
            created_at__gte=one_day_ago
        ).count()

        if articles_count_today >= 3:
            messages.error(self.request, 'Вы не можете публиковать более 3 статей в сутки!')
            return redirect('news_list')

        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author = author
        response = super().form_valid(form)

        # Асинхронная отправка уведомлений подписчикам
        send_notification_to_subscribers.delay(post.id)

        return response

# редактировать статью
class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'  # Требуется право на изменение

    def handle_no_permission(self):
        messages.warning(self.request, 'У вас нет прав на редактирование статей.')
        return redirect('news_list')

    def get_queryset(self):
        # Пользователь может редактировать только свои статьи
        return Post.objects.filter(post_type='AR', author__user=self.request.user)


# удаление статьи
class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'  # Требуется право на удаление

    def handle_no_permission(self):
        messages.warning(self.request, 'У вас нет прав на удаление статей.')
        return redirect('news_list')

    def get_queryset(self):
        # Пользователь может удалять только свои статьи
        return Post.objects.filter(post_type='AR', author__user=self.request.user)