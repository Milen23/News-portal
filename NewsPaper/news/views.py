from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from .models import Post, Author
from .filters import NewsFilter
from .forms import PostForm
from django.shortcuts import render
from django.shortcuts import redirect
from .models import Comment


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
class NewsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        # Получаем или создаем автора для текущего пользователя
        author, created = Author.objects.get_or_create(user=self.request.user)

        # Устанавливаем тип поста как "новость"
        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author = author
        post.save()  # Сохраняем пост, чтобы получить ID

        # Теперь сохраняем связи с категориями (многие ко многим)
        form.save_m2m()  # Эта функция сохраняет связи ManyToMany

        return super().form_valid(form)

# редактировать новость
class NewsUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')


# удаление новости
class NewsDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')


# создание статьи
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        # Получаем или создаем автора для текущего пользователя
        author, created = Author.objects.get_or_create(user=self.request.user)

        # Устанавливаем тип поста как "статья"
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author = author
        post.save()  # Сохраняем пост, чтобы получить ID

        # Сохраняем связи с категориями
        form.save_m2m()

        return super().form_valid(form)

# редактировать статью
class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')


# удаление статьи
class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')