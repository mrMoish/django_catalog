from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product


class CatalogPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Смартфоны")
        cls.product = Product.objects.create(
            name="Смартфон Alpha X",
            description="Х" * 150,
            category=cls.category,
            price="29990.00",
        )

    def test_product_detail_url(self):
        self.assertEqual(
            reverse("catalog:product_detail", args=[self.product.pk]),
            f"/products/{self.product.pk}/",
        )

    def test_product_detail_shows_product(self):
        response = self.client.get(
            reverse("catalog:product_detail", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], self.product)
        self.assertContains(response, "Смартфон Alpha X")
        self.assertContains(response, "Х" * 150)
        self.assertContains(response, "29990")

    def test_product_detail_404(self):
        response = self.client.get(reverse("catalog:product_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_home_lists_products_with_truncated_description(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Смартфон Alpha X")
        self.assertNotContains(response, "Х" * 150)
        self.assertContains(
            response, reverse("catalog:product_detail", args=[self.product.pk])
        )

    def test_templates_inherit_base(self):
        for name, args in [
            ("catalog:home", []),
            ("catalog:contacts", []),
            ("catalog:product_detail", [self.product.pk]),
        ]:
            response = self.client.get(reverse(name, args=args))
            self.assertTemplateUsed(response, "catalog/base.html")
            self.assertTemplateUsed(response, "catalog/includes/navbar.html")
            self.assertTemplateUsed(response, "catalog/includes/footer.html")
