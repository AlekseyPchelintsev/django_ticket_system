from django.urls import path
from . import views


urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),  # /tickets/
    path('create/', views.ticket_create, name='ticket_create'),  # /tickets/create/
    path('<int:ticket_id>/send_message/', views.send_message, name='send_message'),
    path('<int:pk>/update/', views.ticket_update, name='ticket_update'),  # /tickets/<id>/update/
    path('tickets/<int:pk>/delete/', views.delete_ticket, name='delete_ticket'),  # /tickets/<id>/delete/
    path('<int:ticket_id>/status/', views.change_ticket_status, name='change_ticket_status'),
    path('tickets/<int:ticket_id>/mark_as_read/', views.mark_as_read, name='mark_as_read'),
    path('tickets/ticket_closed/', views.ticket_closed, name='ticket_closed'),
    path('tickets/<int:ticket_id>/mark_as_read/', views.mark_as_read, name='mark_as_read'),
]
