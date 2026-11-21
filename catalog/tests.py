from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from users.models import User


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

    def setUp(self):
        # Страницы управления продуктами доступны только авторизованным.
        self.client.force_login(User.objects.create_user("tester@example.com", "Str0ng-pass-123"))

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


class ProductFormValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Смартфоны")

    def make_form(self, **overrides):
        from catalog.forms import ProductForm

        data = {
            "name": "Смартфон Gamma",
            "description": "Хороший смартфон",
            "category": self.category.pk,
            "price": "100.00",
        }
        data.update(overrides)
        return ProductForm(data=data)

    def test_valid_form(self):
        self.assertTrue(self.make_form().is_valid())

    def test_forbidden_words_in_name_any_case(self):
        from catalog.forms import FORBIDDEN_WORDS

        for word in FORBIDDEN_WORDS:
            for variant in (word, word.upper(), word.capitalize()):
                with self.subTest(word=variant):
                    form = self.make_form(name=f"Супер {variant} предложение")
                    self.assertFalse(form.is_valid())
                    self.assertIn("name", form.errors)
                    self.assertIn(word, form.errors["name"][0])

    def test_forbidden_words_in_description_any_case(self):
        from catalog.forms import FORBIDDEN_WORDS

        for word in FORBIDDEN_WORDS:
            with self.subTest(word=word):
                form = self.make_form(description=f"Тут {word.upper()}!")
                self.assertFalse(form.is_valid())
                self.assertIn("description", form.errors)

    def test_empty_description_is_allowed(self):
        self.assertTrue(self.make_form(description="").is_valid())

    def test_negative_price_rejected_with_message(self):
        form = self.make_form(price="-5")
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)
        self.assertIn("не может быть отрицательной", form.errors["price"][0])
        self.assertIn("-5", form.errors["price"][0])

    def test_zero_price_is_allowed(self):
        self.assertTrue(self.make_form(price="0").is_valid())

    def test_fields_are_styled(self):
        form = self.make_form()
        self.assertIn("form-control", form.fields["name"].widget.attrs["class"])
        self.assertIn("form-control", form.fields["description"].widget.attrs["class"])
        self.assertIn("form-control", form.fields["image"].widget.attrs["class"])
        self.assertIn("form-control", form.fields["price"].widget.attrs["class"])
        self.assertIn("form-select", form.fields["category"].widget.attrs["class"])

    def test_checkbox_styled_as_form_check(self):
        from catalog.forms import ProductForm

        product = Product.objects.create(
            name="С картинкой", category=self.category, price="1", image="x.jpg"
        )
        form = ProductForm(instance=product)
        self.assertEqual(
            form.fields["clear_image"].widget.attrs["class"], "form-check-input"
        )

    def test_invalid_fields_get_is_invalid_class(self):
        form = self.make_form(price="-1")
        form.is_valid()
        self.assertIn("is-invalid", form.fields["price"].widget.attrs["class"])
        self.assertNotIn("is-invalid", form.fields["name"].widget.attrs["class"])


class ProductCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Ноутбуки")
        cls.product = Product.objects.create(
            name="Ноутбук Pro", description="Мощный", category=cls.category, price="999.00"
        )

    def setUp(self):
        # Страницы управления продуктами доступны только авторизованным.
        self.client.force_login(User.objects.create_user("tester@example.com", "Str0ng-pass-123"))

    def payload(self, **overrides):
        data = {
            "name": "Новый продукт",
            "description": "Описание",
            "category": self.category.pk,
            "price": "10.50",
        }
        data.update(overrides)
        return data

    def test_create_get_renders_form(self):
        response = self.client.get(reverse("catalog:product_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="form-control"', count=None)
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_create_product(self):
        response = self.client.post(reverse("catalog:product_create"), self.payload())
        created = Product.objects.get(name="Новый продукт")
        self.assertRedirects(
            response, reverse("catalog:product_detail", args=[created.pk])
        )
        self.assertEqual(str(created.price), "10.50")

    def test_create_with_forbidden_word_shows_error(self):
        response = self.client.post(
            reverse("catalog:product_create"), self.payload(name="Онлайн КАЗИНО")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "запрещённые слова: казино")
        self.assertFalse(Product.objects.filter(name="Онлайн КАЗИНО").exists())

    def test_create_with_negative_price_shows_error(self):
        response = self.client.post(
            reverse("catalog:product_create"), self.payload(price="-1")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цена не может быть отрицательной")
        self.assertEqual(Product.objects.count(), 1)

    def test_update_product(self):
        url = reverse("catalog:product_update", args=[self.product.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, self.payload(name="Ноутбук Pro Max"))
        self.assertRedirects(
            response, reverse("catalog:product_detail", args=[self.product.pk])
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Ноутбук Pro Max")

    def test_update_with_forbidden_description_rejected(self):
        url = reverse("catalog:product_update", args=[self.product.pk])
        response = self.client.post(url, self.payload(description="Крипта дешево"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "запрещённые слова")
        self.product.refresh_from_db()
        self.assertEqual(self.product.description, "Мощный")

    def test_delete_product(self):
        url = reverse("catalog:product_delete", args=[self.product.pk])
        self.assertContains(self.client.get(url), "Ноутбук Pro")
        response = self.client.post(url)
        self.assertRedirects(response, reverse("catalog:home"))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_update_and_delete_404(self):
        for name in ("catalog:product_update", "catalog:product_delete"):
            self.assertEqual(self.client.get(reverse(name, args=[9999])).status_code, 404)

    def test_clear_image_checkbox_removes_image(self):
        self.product.image = "catalog/products/x.jpg"
        self.product.save()
        url = reverse("catalog:product_update", args=[self.product.pk])
        self.assertContains(self.client.get(url), "Удалить текущее изображение")
        self.client.post(url, self.payload(clear_image="on"))
        self.product.refresh_from_db()
        self.assertFalse(self.product.image)
