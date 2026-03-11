import logging
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.sites.models import Site
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from news.models import Post, Category

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    """Еженедельная рассылка новых статей подписчикам"""
    # Вычисляем дату неделю назад
    week_ago = timezone.now() - timedelta(days=7)

    # Получаем все категории
    categories = Category.objects.all()

    for category in categories:
        # Получаем новые статьи в этой категории за последнюю неделю
        new_posts = Post.objects.filter(
            categories=category,
            created_at__gte=week_ago
        ).order_by('-created_at')

        # Если есть новые статьи
        if new_posts.exists():
            # Получаем подписчиков категории
            subscribers = category.subscribers.all()

            for subscriber in subscribers:
                if subscriber.email:
                    try:
                        site = Site.objects.get_current()

                        context = {
                            'username': subscriber.username,
                            'category': category,
                            'posts': new_posts,
                            'site': site,
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
                            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@newsportal.com',
                            to=[subscriber.email],
                        )
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        logger.info(
                            f"Отправлена рассылка пользователю {subscriber.username} по категории {category.name}")

                    except Exception as e:
                        logger.error(f"Ошибка при отправке рассылки: {e}")


class Command(BaseCommand):
    help = "Запускает еженедельную рассылку новостей"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Добавляем задачу на каждое воскресенье в 10:00
        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(
                day_of_week='sun',  # воскресенье
                hour=10,
                minute=0,
            ),
            id="weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )

        logger.info("Запущен планировщик еженедельной рассылки")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика")
            scheduler.shutdown()