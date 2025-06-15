from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password


class LoginUserForm(AuthenticationForm):

    username = forms.CharField(label="Логин",
                            widget=forms.TextInput(attrs={'class': 'form-input'}))

    password = forms.CharField(label="Пароль",
                               widget=forms.PasswordInput(attrs={'class': 'form-input'}))


    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(forms.ModelForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        #fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
        fields = ['username', 'password', 'password2']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Пароли не совпадают")
        return cd['password']

class PasswordForm(forms.Form):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        help_text="Введите ваш пароль для подтверждения"
    )

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    new_password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    confirm_password = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Неверный текущий пароль")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Новые пароли не совпадают")

        return cleaned_data