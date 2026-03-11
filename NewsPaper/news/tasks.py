from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from .models import Post, Category
import logging

logger = logging.getLogger(__name__)



@shared_task
def test_redis_connection():
    """Тестовая задача для проверки Redis"""
    print("✅ Тестовая задача выполнена успешно!")
    return "Redis работает!"

@shared_task
def send_notification_to_subscribers(post_id):
    """
    Асинхронная отправка уведомлений подписчикам при создании новой статьи
    """
    try:
        post = Post.objects.get(id=post_id)
        categories = post.categories.all()

        # Собираем всех подписчиков
        subscribers = User.objects.none()
        for category in categories:
            subscribers = subscribers | category.subscribers.all()
        subscribers = subscribers.distinct()

        # Получаем текущий сайт для ссылок
        try:
            site = Site.objects.get_current()
            domain = site.domain
        except:
            domain = '127.0.0.1:8000'

        # Отправляем письма
        for subscriber in subscribers:
            if subscriber.email:
                try:
                    html_content = render_to_string(
                        'email/new_post_notification.html',
                        {
                            'username': subscriber.username,
                            'post': post,
                            'categories': categories,
                            'domain': domain,
                        }
                    )

                    text_content = render_to_string(
                        'email/new_post_notification.txt',
                        {
                            'username': subscriber.username,
                            'post': post,
                            'categories': categories,
                            'domain': domain,
                        }
                    )

                    subject = f'Новая статья: {post.title[:50]}...' if len(
                        post.title) > 50 else f'Новая статья: {post.title}'

                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email='noreply@newsportal.com',
                        to=[subscriber.email],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    logger.info(f"Уведомление отправлено пользователю {subscriber.username}")

                except Exception as e:
                    logger.error(f"Ошибка при отправке пользователю {subscriber.username}: {e}")

        return f"Уведомления отправлены {subscribers.count()} подписчикам"

    except Post.DoesNotExist:
        logger.error(f"Пост с id {post_id} не найден")
        return f"Пост с id {post_id} не найден"
    except Exception as e:
        logger.error(f"Ошибка в send_notification_to_subscribers: {e}")
        return f"Ошибка: {e}"


@shared_task
def send_weekly_newsletter():
    """
    Еженедельная рассылка новых статей (каждый понедельник в 8:00)
    """
    try:
        # Вычисляем дату неделю назад
        week_ago = timezone.now() - timedelta(days=7)

        # Получаем текущий сайт
        try:
            site = Site.objects.get_current()
            domain = site.domain
        except:
            domain = '127.0.0.1:8000'

        # Получаем все категории
        categories = Category.objects.all()
        total_sent = 0

        for category in categories:
            # Получаем новые статьи в этой категории за последнюю неделю
            new_posts = Post.objects.filter(
                categories=category,
                created_at__gte=week_ago
            ).order_by('-created_at')

            if new_posts.exists():
                subscribers = category.subscribers.all()

                for subscriber in subscribers:
                    if subscriber.email:
                        try:
                            context = {
                                'username': subscriber.username,
                                'category': category,
                                'posts': new_posts,
                                'domain': domain,
                                'week_ago': week_ago.strftime('%d.%m.%Y'),
                                'today': timezone.now().strftime('%d.%m.%Y'),
                            }

                            html_content = render_to_string(
                                'email/weekly_newsletter.html',
                                context
                            )

                            text_content = render_to_string(
                                'email/weekly_newsletter.txt',
                                context
                            )

                            msg = EmailMultiAlternatives(
                                subject=f'Еженедельная рассылка: новые статьи в разделе "{category.name}"',
                                body=text_content,
                                from_email='noreply@newsportal.com',
                                to=[subscriber.email],
                            )
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()

                            total_sent += 1
                            logger.info(
                                f"Рассылка отправлена пользователю {subscriber.username} по категории {category.name}")

                        except Exception as e:
                            logger.error(f"Ошибка при отправке рассылки пользователю {subscriber.username}: {e}")

        logger.info(f"Еженедельная рассылка завершена. Отправлено писем: {total_sent}")
        return f"Еженедельная рассылка завершена. Отправлено писем: {total_sent}"

    except Exception as e:
        logger.error(f"Ошибка в send_weekly_newsletter: {e}")
        return f"Ошибка: {e}"


@shared_task
def send_welcome_email(user_id):
    """
    Отправка приветственного письма после регистрации
    """
    try:
        user = User.objects.get(id=user_id)

        try:
            site = Site.objects.get_current()
            domain = site.domain
        except:
            domain = '127.0.0.1:8000'

        context = {
            'username': user.username,
            'domain': domain,
        }

        html_content = render_to_string('email/welcome_email.html', context)
        text_content = render_to_string('email/welcome_email.txt', context)

        msg = EmailMultiAlternatives(
            subject='Добро пожаловать на News Portal!',
            body=text_content,
            from_email='noreply@newsportal.com',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Приветственное письмо отправлено пользователю {user.username}")
        return f"Приветственное письмо отправлено пользователю {user.username}"

    except User.DoesNotExist:
        logger.error(f"Пользователь с id {user_id} не найден")
        return f"Пользователь с id {user_id} не найден"
    except Exception as e:
        logger.error(f"Ошибка в send_welcome_email: {e}")
        return f"Ошибка: {e}"


