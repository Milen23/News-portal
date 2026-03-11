from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site


class CustomAccountAdapter(DefaultAccountAdapter):
    """Кастомный адаптер для отправки дополнительных писем"""

    def send_mail(self, template_prefix, email, context):
        """Отправляет письмо с подтверждением"""
        # Получаем текущий сайт
        site = Site.objects.get_current()
        context['site'] = site
        context['site_name'] = site.name

        # Вызываем стандартный метод allauth
        super().send_mail(template_prefix, email, context)

        # Здесь можно добавить отправку дополнительного письма
        # если нужно

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """Отправка письма с подтверждением"""
        # Стандартный метод allauth, можно кастомизировать
        super().send_confirmation_mail(request, emailconfirmation, signup)

        # Если хочешь отправить дополнительное письмо после подтверждения
        # можно добавить логику здесь

    def confirm_email(self, request, email_address):
        """Действия после подтверждения email"""
        super().confirm_email(request, email_address)

        # Можно отправить приветственное письмо после подтверждения
        if email_address.user:
            self.send_welcome_email(email_address.user)

    def send_welcome_email(self, user):
        """Отправка приветственного письма после активации"""
        site = Site.objects.get_current()

        context = {
            'user': user,
            'site': site,
            'site_name': site.name,
        }

        # Тема письма
        subject = f"Добро пожаловать на {site.name}!"

        # HTML-версия
        html_message = render_to_string('account/email/welcome_email.html', context)

        # Текстовая версия
        text_message = render_to_string('account/email/welcome_email.txt', context)

        # Отправляем письмо
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()