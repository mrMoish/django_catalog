from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from catalog.forms import ProductForm
from catalog.models import Product


def home(request):
    """Контроллер домашней страницы: выводит список всех товаров."""
    products = Product.objects.all()
    return render(request, "catalog/home.html", {"products": products})


@login_required
def product_detail(request, pk):
    """Контроллер страницы с подробной информацией о товаре."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})


def contacts(request):
    """Контроллер страницы с контактной информацией."""
    return render(request, "catalog/contacts.html")


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание продукта."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_message = "Продукт «%(name)s» успешно создан."

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование продукта."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_message = "Продукт «%(name)s» успешно обновлён."

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление продукта с подтверждением."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f"Продукт «{name}» удалён.")
        return response
