# Generated by Django 5.1.4 on 2024-12-27 06:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='last_checked',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Последнее посещение'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('open', 'Открыт'), ('closed', 'Закрыт')], default='open', max_length=10, verbose_name='Статус'),
        ),
    ]
