from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()


class AdminLoginForm(forms.Form):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите username'
    }))
    password = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Введите password'
        }))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            superusers = User.objects.filter(is_superuser=True)
            if not superusers.exists():
                raise forms.ValidationError('Такого пользователя нет')
            if not check_password(password, superusers[0].password):
                raise forms.ValidationError('Неверный пароль')
            admin = authenticate(username=username, password=password)
            if not admin:
                raise forms.ValidationError('Данный пользователь неактивен')
        return super().clean(*args, **kwargs)
