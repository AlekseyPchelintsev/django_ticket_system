from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    # Убираем обязательность поля username, так как используется email
    email = forms.EmailField(required=True, label="Электронная почта")
    
    # Перепишем поле пароля, если требуется дополнительная валидация
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        label="Пароль"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'}),
        label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    # Дополнительная валидация
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email

    def save(self, commit=True):
        # Сохраняем пользователя с паролем
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Устанавливаем пароль
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        # Проверяем, был ли изменен email
        if user.email != self.instance.email:
            user.username = user.email  # Обновляем username с новым значением email
        
        if commit:
            user.save()  # Сохраняем изменения в базе данных
        return user
    

class UserEditForm(forms.ModelForm):
    new_password = forms.CharField(
        max_length=128, 
        required=False, 
        label="Новый пароль", 
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_superuser']

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
    

class AddUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    username = forms.CharField(required=False)  # Добавляем поле username
    role = forms.ChoiceField(choices=[('client', 'Клиент'), ('admin', 'Администратор')], required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Устанавливаем пароль

        # Если поле username пустое, используем email в качестве username
        if not user.username:
            user.username = self.cleaned_data['email']

        # Устанавливаем роль по умолчанию, если не указана
        if not self.cleaned_data.get('role'):
            user.role = 'client'  # Устанавливаем роль клиента по умолчанию

        if commit:
            user.save()
        return user