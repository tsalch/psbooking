from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Min, Q
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode

from utils.models import generate_unique_slug


class Country(models.Model):
    title = models.CharField(max_length=250, default='', unique=True, verbose_name='Страна')
    slug = models.SlugField(max_length=210, default='', blank=True)
    picture = models.ImageField(upload_to='hotels/countries/', blank=True, null=True, verbose_name='Фото')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Country, self.title)
        super().save(*args, **kwargs)

    @property
    def picture_url(self):
        return self.picture.url if self.picture else f'{settings.STATIC_URL}images/destination/destination4.jpg'

    @property
    def fmin_price(self):
        hl = self.hotels.all()
        rdict = Room.objects.filter(hotel__in=hl).aggregate(Min('price')) if hl.count() > 0 else {}
        min_price = rdict.get('price__min', 0)
        return min_price

    class Meta:
        verbose_name_plural = 'Страны'
        verbose_name = 'Страна'


class Town(models.Model):
    title = models.CharField(max_length=250, default='', unique=True, verbose_name='Город')
    country = models.ForeignKey(Country, null=False, on_delete=models.CASCADE, related_name='towns',
                                verbose_name=Country._meta.verbose_name)
    slug = models.SlugField(max_length=210, default='', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Town, self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Города'
        verbose_name = 'Город'


class Option(models.Model):
    title = models.CharField(max_length=250, default='', verbose_name='Сервис')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Опции'
        verbose_name = 'Опция'


def get_upload_to_hotel(instance, filename):
    full_file_name = 'hotels/hotels'
    return get_upload_to(instance, filename, full_file_name, 0, True)


def get_upload_to_room(instance, filename):
    full_file_name = 'hotels/rooms'
    full_file_name = get_upload_to(instance.hotel, filename, full_file_name, 0, False)
    return get_upload_to(instance, filename, full_file_name, 1, True)


def get_upload_to(instance, filename, full_file_name, ind, is_end):
    attrs = (('country', 'town'), ('hotel',))
    for attr in attrs[ind]:
        if instance.__getattribute__(attr):
            if instance.__getattribute__(attr).slug:
                full_file_name += f'/{instance.__getattribute__(attr).slug}'
            else:
                full_file_name += f'/{slugify(unidecode(instance.__getattribute__(attr).title), allow_unicode=True)}'
    if is_end: full_file_name += f'/{filename}'
    return full_file_name


class Hotel(models.Model):
    title = models.CharField(max_length=250, default='', verbose_name='Название')
    picture = models.ImageField(upload_to=get_upload_to_hotel, blank=True, null=True, verbose_name='Фотография отеля')
    category = models.PositiveSmallIntegerField(verbose_name='Категория (звездность)')
    is_renovated = models.BooleanField(default=False, verbose_name='Недавно отремонтирован')
    options = models.ManyToManyField(Option, related_name='hotels', verbose_name=Option._meta.verbose_name)
    description = models.TextField(max_length=2000, default='', blank=False, verbose_name='Описание')
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE, related_name='hotels',
                                verbose_name=Country._meta.verbose_name)
    town = models.ForeignKey(Town, null=True, blank=True, on_delete=models.CASCADE, related_name='hotels',
                             verbose_name=Town._meta.verbose_name)
    slug = models.SlugField(max_length=210, default='', blank=True)

    def __str__(self):
        return self.title

    @property
    def picture_url(self):
        return self.picture.url if self.picture else f'{settings.STATIC_URL}images/rooms/list3.jpg'

    def get_absolute_url(self):
        return reverse('hotels:hotel_booking', args=[str(self.pk)])

    def get_url_update(self):
        return reverse('hotels:hotel_update', args=[str(self.pk)])

    @property
    def favg_rate(self):
        avg_rate = self.reviews.aggregate(models.Avg('rate'))['rate__avg']
        if not avg_rate: avg_rate = 0
        return round(avg_rate, 1)

    def is_available(self, dstart, dend, person):
        qs = self.rooms
        qs = qs.filter(capacity=person) if person else qs.all()
        for room in qs:
            if room.is_available(dstart, dend): return True
        return False

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Hotel, self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Отели'
        verbose_name = 'Отель'


class Room(models.Model):
    ROOM_CLASS_COMFORT = 'c'
    ROOM_CLASS_JS = 'j'
    ROOM_CLASS_LUXURY = 'l'

    ROOM_CLASS_CHOICES = (
        (ROOM_CLASS_COMFORT, 'Комфорт'),
        (ROOM_CLASS_JS, 'Полулюкс'),
        (ROOM_CLASS_LUXURY, 'Люкс'),
    )
    room_class_dict = {rc[0]: rc[1] for rc in ROOM_CLASS_CHOICES}
    hotel = models.ForeignKey(Hotel, null=True, on_delete=models.CASCADE, related_name='rooms',
                              verbose_name=Hotel._meta.verbose_name)
    number = models.IntegerField(verbose_name='№ комнаты')
    room_class = models.CharField(max_length=1, null=True, choices=ROOM_CLASS_CHOICES,
                                  default=ROOM_CLASS_COMFORT, verbose_name='Тип номера')
    capacity = models.PositiveSmallIntegerField(default=1, verbose_name='Вместимость')
    picture = models.ImageField(upload_to=get_upload_to_room, blank=True, null=True, verbose_name='Фотография номера')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена за ночь')
    description = models.TextField(max_length=1000, default='', blank=False, verbose_name='Описание')

    def room_class_vis(self):
        return self.room_class_dict[self.room_class]

    def __str__(self):
        return f'{self.room_class_vis()} № {self.number} в {self.hotel}'

    @property
    def picture_url(self):
        return self.picture.url if self.picture else f'{settings.STATIC_URL}images/rooms/room1.jpg'

    def get_absolute_url(self):
        return reverse('hotels:room_update', args=[str(self.pk)])

    def is_available(self, dstart, dend):
        ocupied = self.reservations.filter(check_out__gte=dstart, check_in__lte=dend)
        ocupied = ocupied.filter(Q(check_in__gte=dstart) and Q(check_in__lte=dend) or
                                 Q(check_in__lt=dstart) and Q(check_out__gte=dstart)).exists()
        return not ocupied

    class Meta:
        verbose_name_plural = 'Комнаты'
        verbose_name = 'Комната'


class Reservation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reservations')
    hotel = models.ForeignKey(Hotel, null=True, on_delete=models.CASCADE, related_name='reservations',
                              verbose_name=Hotel._meta.verbose_name)
    room = models.ForeignKey(Room, null=True, on_delete=models.CASCADE, related_name='reservations',
                             verbose_name=Room._meta.verbose_name)
    created = models.DateField(null=True, auto_now_add=True, verbose_name='Создано')
    check_in = models.DateField(null=True, verbose_name='Дата заезда')
    check_out = models.DateField(null=True, verbose_name='Дата отъезда')

    def __str__(self):
        return f'{self.user} : {self.hotel} : {self.created}'

    def get_absolute_url(self):
        return reverse('hotels:reserv_cancel', args=[str(self.pk)])

    class Meta:
        verbose_name_plural = 'Бронирования'
        verbose_name = 'Бронирование'


class Review(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviews',
                             verbose_name=User._meta.verbose_name)
    hotel = models.ForeignKey(Hotel, null=True, on_delete=models.CASCADE, related_name='reviews',
                              verbose_name=Hotel._meta.verbose_name)
    rate = models.PositiveSmallIntegerField(default=0, verbose_name='Оценка')
    text = models.TextField(max_length=500, default='', blank=False, verbose_name='Текст отзыва')
    created = models.DateField(null=True, auto_now_add=True, verbose_name='Создан')

    def __str__(self):
        return f'{self.user} : {self.hotel} : {self.rate} : {self.created}'

    class Meta:
        verbose_name_plural = 'Отзывы'
        verbose_name = 'Отзыв'
