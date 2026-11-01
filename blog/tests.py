from django.test import TestCase
from django.urls import reverse

from blog.models import BlogPost


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.published = BlogPost.objects.create(
            title="Опубликованная", content="Текст", is_published=True
        )
        cls.draft = BlogPost.objects.create(
            title="Черновик", content="Текст", is_published=False
        )

    def test_urls_end_with_slash(self):
        self.assertEqual(reverse("blog:list"), "/blogs/")
        self.assertEqual(
            reverse("blog:detail", args=[self.published.pk]),
            f"/blogs/{self.published.pk}/",
        )

    def test_list_shows_only_published(self):
        response = self.client.get(reverse("blog:list"))
        self.assertContains(response, "Опубликованная")
        self.assertNotContains(response, "Черновик")

    def test_detail_increments_views(self):
        url = reverse("blog:detail", args=[self.published.pk])
        self.client.get(url)
        self.client.get(url)
        self.published.refresh_from_db()
        self.assertEqual(self.published.views_count, 2)

    def test_update_redirects_to_detail(self):
        response = self.client.post(
            reverse("blog:update", args=[self.published.pk]),
            {"title": "Новое", "content": "Текст", "is_published": "on"},
        )
        self.assertRedirects(
            response, reverse("blog:detail", args=[self.published.pk])
        )

    def test_create_and_delete(self):
        response = self.client.post(
            reverse("blog:create"),
            {"title": "Новая", "content": "Текст", "is_published": "on"},
        )
        self.assertRedirects(response, reverse("blog:list"))
        post = BlogPost.objects.get(title="Новая")
        response = self.client.post(reverse("blog:delete", args=[post.pk]))
        self.assertRedirects(response, reverse("blog:list"))
        self.assertFalse(BlogPost.objects.filter(pk=post.pk).exists())

    def test_templates_inherit_base(self):
        response = self.client.get(reverse("blog:list"))
        self.assertTemplateUsed(response, "catalog/base.html")
        self.assertTemplateUsed(response, "catalog/includes/navbar.html")
