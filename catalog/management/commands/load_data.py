from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Удаляет все продукты и категории и загружает тестовые данные из фикстуры"

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write("Старые данные удалены")

        call_command("loaddata", "catalog_data.json", verbosity=0)
        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены"))
