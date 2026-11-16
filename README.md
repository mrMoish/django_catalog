# Django Catalog 

Учебный проект на Django: каталог товаров со списком на главной, страницей товара и страницей контактов. Вёрстка выполнена на Bootstrap 5.

## Структура

- `config/` — настройки проекта и корневая маршрутизация
- `catalog/` — приложение с контроллерами и шаблонами (`templates/catalog/`)
  - `templates/catalog/base.html` — базовый шаблон (шапка, подвал, стили, блоки `title`, `content`, `extra_css`, `extra_js`)
  - `templates/catalog/includes/` — подшаблоны: главное меню (`navbar.html`), подвал (`footer.html`), изображение товара (`product_image.html`)
  - `static/catalog/css/style.css` — общие стили

## Страницы

| URL                   | Название         | Описание                      |
|-----------------------|------------------|-------------------------------|
| `/`                   | `home`           | Главная: список товаров       |
| `/products/<int:pk>/` | `product_detail` | Подробная информация о товаре |
| `/contacts/`          | `contacts`       | Контактная информация         |

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # укажите параметры PostgreSQL
python manage.py migrate
python manage.py load_data       # тестовые категории и товары
python manage.py runserver
```

После запуска откройте http://127.0.0.1:8000/.

## Процесс разработки (GitFlow)

- `main` — стабильная версия проекта
- `develop` — основная ветка разработки, от неё создаются все остальные
- `homework/<номер>` — отдельная ветка под каждое домашнее задание (например, `homework/django-1`)

Работа над заданием ведётся в ветке `homework/*`, после завершения она вливается в `develop`, а релизная версия из `develop` — в `main`.
