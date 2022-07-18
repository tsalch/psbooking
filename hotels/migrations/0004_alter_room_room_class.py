# Generated by Django 3.2.12 on 2022-03-12 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0003_auto_20220313_0022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_class',
            field=models.CharField(choices=[('c', 'Комфорт'), ('j', 'Полулюкс'), ('l', 'Люкс')], default='c', max_length=1, null=True, verbose_name='Тип номера'),
        ),
    ]