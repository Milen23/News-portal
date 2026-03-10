from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'created_at', 'rating')
    list_filter = ('post_type', 'categories', 'created_at')
    search_fields = ('title', 'content')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'rating')
    list_filter = ('created_at',)
    search_fields = ('text',)

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment, CommentAdmin)