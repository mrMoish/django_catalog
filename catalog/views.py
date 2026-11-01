from django.views.generic import DetailView, ListView, TemplateView

from catalog.models import Product


class HomeView(ListView):
    """Контроллер домашней страницы: выводит список всех товаров."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"


class ProductDetailView(DetailView):
    """Контроллер страницы с подробной информацией о товаре."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ContactsView(TemplateView):
    """Контроллер страницы с контактной информацией."""

    template_name = "catalog/contacts.html"
