from django.shortcuts import render


def home(request):
    """Контроллер домашней страницы."""
    return render(request, "catalog/home.html")


def contacts(request):
    """Контроллер страницы с контактной информацией."""
    return render(request, "catalog/contacts.html")
