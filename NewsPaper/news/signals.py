from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from .models import Post, Category
from django.utils import timezone


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    """Отправка уведомлений подписчикам при создании новой статьи/новости"""
    if created:
        # Получаем все категории этой новости
        categories = instance.categories.all()

        # Собираем всех подписчиков этих категорий (без дубликатов)
        subscribers = User.objects.none()
        for category in categories:
            subscribers = subscribers | category.subscribers.all()
        subscribers = subscribers.distinct()

        # Отправляем письмо каждому подписчику
        for subscriber in subscribers:
            # Проверяем, есть ли у пользователя email
            if subscriber.email:
                html_content = render_to_string(
                    'email/new_post_notification.html',
                    {
                        'username': subscriber.username,
                        'post': instance,
                        'categories': categories,
                    }
                )

                text_content = render_to_string(
                    'email/new_post_notification.txt',
                    {
                        'username': subscriber.username,
                        'post': instance,
                        'categories': categories,
                    }
                )

                # Формируем тему письма
                if len(instance.title) > 50:
                    subject = f'Новая статья: {instance.title[:50]}...'
                else:
                    subject = f'Новая статья: {instance.title}'

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@newsportal.com',
                    to=[subscriber.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()