import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')

# Загружаем конфигурацию
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи
app.autodiscover_tasks()

# Простая настройка расписания
app.conf.beat_schedule = {
    'send-weekly-newsletter': {
        'task': 'news.tasks.send_weekly_newsletter',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')