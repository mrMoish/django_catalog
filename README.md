# Django Catalog 

Учебный проект на Django: каталог товаров со списком на главной, страницей товара и страницей контактов. Вёрстка выполнена на Bootstrap 5.

## Структура

- `config/` — настройки проекта и корневая маршрутизация
- `users/` — пользователи: модель `User` (наследник `AbstractUser`, вход по email; поля `avatar`, `phone`, `country`), регистрация, вход, выход
- `catalog/` — приложение с контроллерами и шаблонами (`templates/catalog/`)
  - `templates/catalog/base.html` — базовый шаблон (шапка, подвал, стили, блоки `title`, `content`, `extra_css`, `extra_js`)
  - `forms.py` — форма продукта `ProductForm` (валидация и стилизация полей)
  - `templates/catalog/includes/` — подшаблоны: главное меню (`navbar.html`), подвал (`footer.html`), изображение товара (`product_image.html`), поле формы (`form_field.html`)
  - `static/catalog/css/style.css` — общие стили

## Страницы

| URL                   | Название         | Описание                      |
|-----------------------|------------------|-------------------------------|
| `/`                   | `home`           | Главная: список товаров       |
| `/products/<int:pk>/` | `product_detail` | Подробная информация о товаре |
| `/contacts/`          | `contacts`       | Контактная информация         |
| `/products/create/`   | `product_create` | Создание продукта             |
| `/products/<int:pk>/update/` | `product_update` | Редактирование продукта |
| `/products/<int:pk>/delete/` | `product_delete` | Удаление продукта (с подтверждением) |
| `/users/register/`    | `users:register` | Регистрация (email, пароль, подтверждение) + приветственное письмо |
| `/users/login/`       | `users:login`    | Вход по email и паролю        |
| `/users/logout/`      | `users:logout`   | Выход (POST)                  |

Доступ: анонимным пользователям открыты главная, контакты, регистрация и вход. Страницы продукта (просмотр, создание, изменение, удаление) требуют входа — `login_required` / `LoginRequiredMixin`, анонимы перенаправляются на `/users/login/`.

| `/products/<int:pk>/unpublish/` | `product_unpublish` | Снятие с публикации (POST, право `can_unpublish_product`) |

## Формы и валидация

- Форма `ProductForm` построена на `django.forms.ModelForm`.
- Запрещённые слова вынесены в константу `FORBIDDEN_WORDS` (`catalog/forms.py`); название и описание проверяются без учёта регистра (`clean_name`, `clean_description`).
- Цена проверяется в `clean_price`: отрицательное значение вызывает `ValidationError` с понятным сообщением.
- Bootstrap-классы полям назначаются в `__init__` (`form-control`, `form-select`, `form-check-input` для чекбоксов); поля с ошибками подсвечиваются `is-invalid`.

## Почта

По умолчанию письма выводятся в консоль. Чтобы слать через SMTP, задайте в `.env` `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` (см. `.env.example`).

## Права доступа и модерация

- У `Product` есть поле `is_published` (`BooleanField`, по умолчанию `False`) и `owner` (`ForeignKey` на пользователя). При создании `owner` заполняется текущим пользователем в `ProductCreateView.form_valid`; создавать продукты могут только авторизованные.
- Кастомное право модели: `can_unpublish_product` — «Может отменять публикацию продукта».
- Группа «Модератор продуктов» создаётся командой (после `migrate`): `python manage.py create_moderator_group`. Права группы: `can_unpublish_product` и `delete_product`.
- Редактировать продукт может владелец или модератор (право `can_unpublish_product`), удалять — владелец или обладатель права `delete_product`. Остальные получают 403, анонимы — редирект на вход. Проверки собраны в методах модели `can_be_edited_by` / `can_be_deleted_by` и используются в контроллерах (`UserPassesTestMixin`) и в шаблоне (кнопки «Редактировать», «Удалить», «Снять с публикации»).
- Неопубликованные продукты видят только их владельцы и модераторы.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # укажите параметры PostgreSQL
python manage.py migrate         # при первом запуске после появления users — на чистой БД
python manage.py load_data       # тестовые категории и товары
python manage.py create_moderator_group   # группа «Модератор продуктов»
python manage.py createsuperuser # пользователи также создаются через /admin/
python manage.py runserver
```

После запуска откройте http://127.0.0.1:8000/.

## Процесс разработки (GitFlow)

- `main` — стабильная версия проекта
- `develop` — основная ветка разработки, от неё создаются все остальные
- `homework/<номер>` — отдельная ветка под каждое домашнее задание (например, `homework/django-1`)

Работа над заданием ведётся в ветке `homework/*`, после завершения она вливается в `develop`, а релизная версия из `develop` — в `main`.
