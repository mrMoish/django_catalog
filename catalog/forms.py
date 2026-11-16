from django import forms

from catalog.models import Product

# Слова, которые нельзя использовать в названии и описании продукта.
# Проверка не чувствительна к регистру.
FORBIDDEN_WORDS = (
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
)


def find_forbidden_words(text):
    """Возвращает список запрещённых слов, найденных в тексте (без учёта регистра)."""
    lowered = (text or "").casefold()
    return [word for word in FORBIDDEN_WORDS if word in lowered]


class StyledFormMixin:
    """Подключает к полям формы стили Bootstrap 5, принятые на сайте."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css_class}".strip()

    def full_clean(self):
        super().full_clean()
        # Подсвечиваем поля с ошибками красной рамкой Bootstrap.
        if self.is_bound:
            for name in self._errors or {}:
                field = self.fields.get(name)
                if field is not None:
                    attrs = field.widget.attrs
                    attrs["class"] = f"{attrs.get('class', '')} is-invalid".strip()


class ProductForm(StyledFormMixin, forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False, label="Удалить текущее изображение"
    )

    class Meta:
        model = Product
        fields = ("name", "description", "image", "category", "price")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Введите наименование"}),
            "description": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Опишите продукт"}
            ),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
            "price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "Выберите категорию"
        # Чекбокс удаления изображения нужен только у продукта с картинкой.
        if not (self.instance.pk and self.instance.image):
            del self.fields["clear_image"]

    def _validate_no_forbidden_words(self, field_name, label):
        value = self.cleaned_data.get(field_name)
        found = find_forbidden_words(value)
        if found:
            raise forms.ValidationError(
                "%(label)s содержит запрещённые слова: %(words)s. "
                "Пожалуйста, уберите их.",
                code="forbidden_words",
                params={"label": label, "words": ", ".join(found)},
            )
        return value

    def clean_name(self):
        return self._validate_no_forbidden_words("name", "Наименование")

    def clean_description(self):
        return self._validate_no_forbidden_words("description", "Описание")

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError(
                "Цена не может быть отрицательной (вы указали %(price)s). "
                "Введите значение 0 или больше.",
                code="negative_price",
                params={"price": price},
            )
        return price

    def save(self, commit=True):
        product = super().save(commit=False)
        if self.cleaned_data.get("clear_image") and not self.files.get("image"):
            product.image.delete(save=False)
        if commit:
            product.save()
        return product
