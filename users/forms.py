from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from catalog.forms import StyledFormMixin

User = get_user_model()


class RegistrationForm(StyledFormMixin, UserCreationForm):
    """Регистрация по email и паролю с подтверждением пароля."""

    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={"placeholder": "name@example.com", "autocomplete": "email"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Email"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["password2"].help_text = "Введите тот же пароль ещё раз."

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        # Уникальность проверяем без учёта регистра.
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует.", code="unique"
            )
        return email


class EmailAuthenticationForm(StyledFormMixin, AuthenticationForm):
    """Вход по паре email и пароль."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Неверный email или пароль. Проверьте введённые данные.",
        "inactive": "Эта учётная запись отключена.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        username = self.fields["username"]
        username.label = "Email"
        username.widget = forms.EmailInput(
            attrs={
                "autofocus": True,
                "placeholder": "name@example.com",
                "autocomplete": "email",
                "class": "form-control",
            }
        )
        self.fields["password"].label = "Пароль"

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()
