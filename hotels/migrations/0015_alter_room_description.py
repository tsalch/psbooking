# Generated by Django 3.2.12 on 2022-04-27 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0014_alter_hotel_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(default='', max_length=1000, verbose_name='Описание'),
        ),
    ]
