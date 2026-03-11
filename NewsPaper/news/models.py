from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum



class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        """Обновление рейтинга автора"""
        # Суммарный рейтинг всех статей автора * 3
        post_rating = self.posts.aggregate(Sum('rating')).get('rating__sum') or 0
        post_rating *= 3

        # Суммарный рейтинг всех комментариев автора
        author_comments_rating = self.user.comments.aggregate(Sum('rating')).get('rating__sum') or 0

        # Суммарный рейтинг комментариев к статьям автора
        comments_to_posts_rating = Comment.objects.filter(post__author=self).aggregate(Sum('rating')).get('rating__sum') or 0

        self.rating = post_rating + author_comments_rating + comments_to_posts_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(
        User,
        related_name='subscribed_categories',
        blank=True
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title} ({self.get_post_type_display()})'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        """Возвращает начало статьи (124 символа + ...)"""
        return self.content[:124] + '...' if len(self.content) > 124 else self.content


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post.title} - {self.category.name}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'Комментарий от {self.user.username} к {self.post.title}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

