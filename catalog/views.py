from django.shortcuts import get_object_or_404, render

from catalog.models import Product


def home(request):
    """Контроллер домашней страницы: выводит список всех товаров."""
    products = Product.objects.all()
    return render(request, "catalog/home.html", {"products": products})


def product_detail(request, pk):
    """Контроллер страницы с подробной информацией о товаре."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})


def contacts(request):
    """Контроллер страницы с контактной информацией."""
    return render(request, "catalog/contacts.html")
