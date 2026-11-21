from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер пользователей, где логином служит email, а не username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Необходимо указать адрес электронной почты.")
        # Приводим email к нижнему регистру целиком, чтобы вход не зависел от регистра.
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields["is_staff"] is not True:
            raise ValueError("У суперпользователя должно быть is_staff=True.")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("У суперпользователя должно быть is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Пользователь, авторизующийся по адресу электронной почты."""

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        error_messages={"unique": "Пользователь с таким email уже существует."},
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Номер телефона",
        help_text="Например, +7 900 123-45-67",
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Страна",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.email
