from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name="Наименование")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(
        upload_to="catalog/products/",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена за покупку"
    )
    is_published = models.BooleanField(
        default=False, verbose_name="Опубликован"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата последнего изменения"
    )

    class Meta:
        verbose_name = "продукт"
        verbose_name_plural = "продукты"
        ordering = ["name"]
        permissions = [
            ("can_unpublish_product", "Может отменять публикацию продукта"),
        ]

    def __str__(self):
        return f"{self.name} ({self.price})"

    # Правила доступа вынесены в модель, чтобы контроллеры и шаблоны
    # опирались на одну и ту же логику.

    def is_owned_by(self, user):
        return user.is_authenticated and self.owner_id == user.pk

    def can_be_edited_by(self, user):
        """Изменять продукт может владелец или модератор."""
        return self.is_owned_by(user) or user.has_perm("catalog.can_unpublish_product")

    def can_be_deleted_by(self, user):
        """Удалять продукт может владелец или тот, у кого есть право удаления."""
        return self.is_owned_by(user) or user.has_perm("catalog.delete_product")

    def can_be_unpublished_by(self, user):
        return self.is_published and user.has_perm("catalog.can_unpublish_product")
