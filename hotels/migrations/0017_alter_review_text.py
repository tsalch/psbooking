# Generated by Django 3.2.12 on 2022-04-28 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0016_alter_review_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(default='', max_length=500, verbose_name='Текст отзыва'),
        ),
    ]
