from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название тикета")
    description = models.TextField(verbose_name="Описание")
    
    def clean(self):
        if len(self.description) > 150:
            raise ValidationError('Описание не должно превышать 150 символов.')
        
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name="Статус")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name="Владелец")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    last_checked = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    
class Message(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='messages', on_delete=models.CASCADE, verbose_name="Тикет")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    content = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    

@receiver(post_save, sender=Message)
def update_ticket_updated_at(sender, instance, **kwargs):
    # Обновляем поле updated_at у тикета, к которому принадлежит сообщение
    instance.ticket.updated_at = timezone.now()
    instance.ticket.save()