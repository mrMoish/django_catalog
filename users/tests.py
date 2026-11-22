from django.core import mail
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from users.models import User


class UserModelTests(TestCase):
    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user("Test@Example.COM", "pass12345!")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("pass12345!"))

    def test_extra_fields(self):
        user = User.objects.create_user(
            "a@b.com", "pass12345!", phone="+7900", country="Россия"
        )
        self.assertEqual(user.phone, "+7900")
        self.assertEqual(user.country, "Россия")


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse("users:register")
        self.data = {
            "email": "new@example.com",
            "password1": "Str0ng-pass-123",
            "password2": "Str0ng-pass-123",
        }

    def test_register_creates_user_sends_mail_and_logs_in(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("catalog:home"))
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])
        self.assertIn("_auth_user_id", self.client.session)

    def test_password_mismatch(self):
        self.data["password2"] = "different-pass-456"
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_duplicate_email_case_insensitive(self):
        User.objects.create_user("new@example.com", "x-pass-12345")
        self.data["email"] = "NEW@example.com"
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, "уже существует")

    def test_weak_password_rejected(self):
        self.data.update(password1="12345678", password2="12345678")
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_invalid_email(self):
        self.data["email"] = "not-an-email"
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_mail_failure_does_not_break_registration(self):
        from unittest import mock

        with mock.patch("users.views.send_mail", side_effect=OSError("smtp down")):
            response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("catalog:home"))
        self.assertTrue(User.objects.filter(email="new@example.com").exists())


class LoginTests(TestCase):
    def setUp(self):
        self.url = reverse("users:login")
        User.objects.create_user("user@example.com", "Str0ng-pass-123")

    def test_login_ok(self):
        response = self.client.post(
            self.url, {"username": "user@example.com", "password": "Str0ng-pass-123"}
        )
        self.assertRedirects(response, reverse("catalog:home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_email_case_insensitive(self):
        response = self.client.post(
            self.url, {"username": "User@Example.com", "password": "Str0ng-pass-123"}
        )
        self.assertRedirects(response, reverse("catalog:home"))

    def test_login_wrong_password_shows_error(self):
        response = self.client.post(
            self.url, {"username": "user@example.com", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный email или пароль")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_unknown_email(self):
        response = self.client.post(
            self.url, {"username": "nobody@example.com", "password": "x"}
        )
        self.assertContains(response, "Неверный email или пароль")

    def test_logout(self):
        self.client.login(username="user@example.com", password="Str0ng-pass-123")
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("catalog:home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class AccessControlTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Тест")
        self.user = User.objects.create_user("u@example.com", "Str0ng-pass-123")
        # Изменять и удалять продукт может только владелец.
        self.product = Product.objects.create(
            name="Товар", category=category, price=10, owner=self.user, is_published=True
        )
        self.protected = [
            reverse("catalog:product_create"),
            reverse("catalog:product_detail", args=[self.product.pk]),
            reverse("catalog:product_update", args=[self.product.pk]),
            reverse("catalog:product_delete", args=[self.product.pk]),
        ]

    def test_anonymous_redirected_to_login(self):
        for url in self.protected:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response, f"{reverse('users:login')}?next={url}"
                )

    def test_anonymous_cannot_post(self):
        self.client.post(reverse("catalog:product_delete", args=[self.product.pk]))
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_product_list_is_public(self):
        self.assertEqual(self.client.get(reverse("catalog:home")).status_code, 200)

    def test_authenticated_has_access(self):
        self.client.login(username="u@example.com", password="Str0ng-pass-123")
        for url in self.protected:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
