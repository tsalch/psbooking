# Generated by Django 3.2.12 on 2022-04-27 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0013_auto_20220427_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='description',
            field=models.TextField(default='', max_length=2000, verbose_name='Описание'),
        ),
    ]