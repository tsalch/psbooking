from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from hotels.models import Country, Town


class Profile(models.Model):
    USER_ROLE_ADMINISTRATOR = 'a'
    USER_ROLE_CONTMANAGER = 'm'
    USER_ROLE_USER = 'u'
    USER_ROLE_CHOICES = (
        (USER_ROLE_ADMINISTRATOR, 'Администратор'),
        (USER_ROLE_CONTMANAGER, 'Контент менеджер'),
        (USER_ROLE_USER, 'Пользователь')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='accounts/profiles/avatar', verbose_name='Аватар')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Телефон')
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE, related_name='profiles',
                                verbose_name=Country._meta.verbose_name)
    town = models.ForeignKey(Town, null=True, blank=True, on_delete=models.CASCADE, related_name='profiles',
                             verbose_name=Town._meta.verbose_name)
    role = models.CharField(max_length=1, null=True, choices=USER_ROLE_CHOICES,
                            default=USER_ROLE_USER, verbose_name='Роль')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile', args=[str(self.pk)])

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else ''
