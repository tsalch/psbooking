# Generated by Django 3.2.12 on 2022-04-03 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0008_alter_reservation_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(blank=True, default='', max_length=700, verbose_name='Отзыв'),
        ),
    ]
