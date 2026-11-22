from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, View

from catalog.forms import ProductForm
from catalog.models import Product


def visible_products(user):
    """Продукты, которые пользователь вправе видеть.

    Все видят опубликованные; владелец дополнительно видит свои неопубликованные,
    модератор (право can_unpublish_product) — все.
    """
    if user.has_perm("catalog.can_unpublish_product"):
        return Product.objects.all()
    if user.is_authenticated:
        return Product.objects.filter(Q(is_published=True) | Q(owner=user))
    return Product.objects.filter(is_published=True)


def home(request):
    """Контроллер домашней страницы: выводит список доступных товаров."""
    products = visible_products(request.user).select_related("category")
    return render(request, "catalog/home.html", {"products": products})


@login_required
def product_detail(request, pk):
    """Контроллер страницы с подробной информацией о товаре."""
    product = get_object_or_404(visible_products(request.user), pk=pk)
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "can_edit": product.can_be_edited_by(request.user),
            "can_delete": product.can_be_deleted_by(request.user),
            "can_unpublish": product.can_be_unpublished_by(request.user),
        },
    )


def contacts(request):
    """Контроллер страницы с контактной информацией."""
    return render(request, "catalog/contacts.html")


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание продукта (только для авторизованных)."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_message = "Продукт «%(name)s» успешно создан."

    def form_valid(self, form):
        # Владелец всегда текущий пользователь, в форме этого поля нет.
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    """Редактирование продукта: только владелец или модератор."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_message = "Продукт «%(name)s» успешно обновлён."

    def test_func(self):
        return self.get_object().can_be_edited_by(self.request.user)

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление продукта с подтверждением: только владелец или модератор."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")

    def test_func(self):
        return self.get_object().can_be_deleted_by(self.request.user)

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f"Продукт «{name}» удалён.")
        return response


class ProductUnpublishView(PermissionRequiredMixin, View):
    """Отмена публикации продукта (только POST, нужно право can_unpublish_product)."""

    permission_required = "catalog.can_unpublish_product"
    http_method_names = ["post"]

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.is_published:
            product.is_published = False
            product.save(update_fields=["is_published", "updated_at"])
            messages.success(
                request, f"Публикация продукта «{product.name}» отменена."
            )
        return redirect("catalog:product_detail", pk=product.pk)
