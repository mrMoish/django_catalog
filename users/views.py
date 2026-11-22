import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import EmailAuthenticationForm, RegistrationForm

logger = logging.getLogger(__name__)


def send_welcome_email(user):
    """Отправляет приветственное письмо. Возвращает True, если письмо ушло."""
    try:
        sent = send_mail(
            subject="Добро пожаловать в Каталог!",
            message=(
                "Здравствуйте!\n\n"
                "Спасибо за регистрацию в Каталоге. Ваша учётная запись "
                f"{user.email} успешно создана.\n\n"
                "Теперь вам доступны создание, редактирование и удаление товаров.\n\n"
                "С уважением, команда Каталога."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Не удалось отправить приветственное письмо на %s", user.email)
        return False
    return bool(sent)


class RegisterView(CreateView):
    """Регистрация: создаёт пользователя, отправляет письмо и сразу авторизует."""

    form_class = RegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        if send_welcome_email(self.object):
            messages.success(
                self.request,
                "Регистрация прошла успешно. Приветственное письмо отправлено "
                f"на {self.object.email}.",
            )
        else:
            messages.warning(
                self.request,
                "Регистрация прошла успешно, но приветственное письмо отправить "
                "не удалось.",
            )
        return response


class UserLoginView(LoginView):
    """Авторизация по email и паролю."""

    authentication_form = EmailAuthenticationForm
    template_name = "users/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    """Выход из учётной записи (POST-запрос)."""

    next_page = reverse_lazy("catalog:home")
