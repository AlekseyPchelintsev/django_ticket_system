from django.urls import path
from .views import (users, 
                    edit_user, 
                    delete_user, 
                    add_user, 
                    register, 
                    user_login, 
                    profile, 
                    edit_profile, 
                    change_password)

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change_password/', change_password, name='change_password'),
    path('users/', users, name='users'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/add/', add_user, name='add_user'),
    path('logout/', LogoutView.as_view(), name='logout')
]
