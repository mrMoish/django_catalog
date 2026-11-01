from django.db.models import F
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.models import BlogPost

POST_FIELDS = ["title", "content", "preview", "is_published"]


class PostListView(ListView):
    """Список статей: только опубликованные."""

    model = BlogPost

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class PostDetailView(DetailView):
    """Просмотр статьи: увеличивает счётчик просмотров."""

    model = BlogPost

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        BlogPost.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        obj.refresh_from_db()
        return obj


class PostCreateView(CreateView):
    model = BlogPost
    fields = POST_FIELDS
    success_url = reverse_lazy("blog:list")


class PostUpdateView(UpdateView):
    """Редактирование: после сохранения — на страницу статьи."""

    model = BlogPost
    fields = POST_FIELDS

    def get_success_url(self):
        return reverse("blog:detail", args=[self.object.pk])


class PostDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy("blog:list")
