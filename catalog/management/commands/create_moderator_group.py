from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from catalog.models import Product

GROUP_NAME = "Модератор продуктов"

# Коды прав, которые получает модератор.
PERMISSION_CODENAMES = ("can_unpublish_product", "delete_product")


class Command(BaseCommand):
    help = (
        "Создаёт группу «Модератор продуктов» и назначает ей права "
        "can_unpublish_product и delete_product (можно запускать повторно)"
    )

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name=GROUP_NAME)

        permissions = Permission.objects.filter(
            content_type__app_label=Product._meta.app_label,
            content_type__model=Product._meta.model_name,
            codename__in=PERMISSION_CODENAMES,
        )
        if permissions.count() != len(PERMISSION_CODENAMES):
            self.stderr.write(
                self.style.ERROR(
                    "Права не найдены. Сначала выполните: python manage.py migrate"
                )
            )
            return

        group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f"Группа «{GROUP_NAME}» {'создана' if created else 'обновлена'}: "
                + ", ".join(sorted(PERMISSION_CODENAMES))
            )
        )
