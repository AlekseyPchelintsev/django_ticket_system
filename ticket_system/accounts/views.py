from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, update_session_auth_hash
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .forms import AddUserForm, UserEditForm, UserRegistrationForm, UserLoginForm, User, ProfileEditForm
from django.http import HttpResponseForbidden


def admin_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return HttpResponseForbidden("У вас нет доступа к этой странице.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# redirect
def home(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')

            # Если поле username пустое, используем email в качестве username
            if not username:
                username = email

            # Проверка на уникальность username
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Имя пользователя уже занято.')
                return render(request, 'accounts/register.html', {'form': form})

            # Создание пользователя
            try:
                user = form.save(commit=False)  # Не сохраняем еще в БД
                user.username = username  # Устанавливаем username
                user.save()  # Сохраняем пользователя
                return redirect('login')  # Перенаправление на страницу входа
            except IntegrityError:
                form.add_error('username', 'Ошибка при регистрации. Попробуйте еще раз.')
                return render(request, 'accounts/register.html', {'form': form})

    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(instance=request.user, data=request.POST)
        if form.is_valid():
            # Обновляем email и username (если email был изменен)
            new_email = form.cleaned_data['email']
            
            # Если email изменился, обновляем username
            if request.user.username != new_email:
                request.user.username = new_email  # Обновляем поле username
                request.user.email = new_email     # Обновляем поле email
            
            form.save()  # Сохраняем изменения в модели пользователя
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Обновление сессии пользователя
            return redirect('profile')
        else:
            # Передача ошибок обратно в шаблон
            return render(request, 'accounts/change_password.html', {'form': form})
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
@admin_only
def users(request):
    users = User.objects.all()
    return render(request, 'accounts/users.html', {'users': users})


@login_required
@admin_only
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = UserEditForm(instance=user, data=request.POST)
        if form.is_valid():
            # Получаем новый email из формы
            new_email = form.cleaned_data['email']
            
            # Если email изменился, обновляем username
            if user.username != new_email:
                user.username = new_email  # Обновляем поле username
                user.email = new_email     # Обновляем поле email
            
            # Сохраняем изменения
            form.save()
            return redirect('users')  # Перенаправление на страницу с пользователями
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'accounts/edit_user.html', {'form': form})


@login_required
@admin_only
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('users')


@login_required
@admin_only
def add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
    else:
        form = AddUserForm()
    return render(request, 'accounts/add_user.html', {'form': form})