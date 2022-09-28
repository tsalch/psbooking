from django.contrib import admin

# Register your models here.
from . import models


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Town)
class TownAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Option)
class OptionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Hotel)
class HotelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'room', 'check_in', 'check_out']
    list_select_related = ['user', 'hotel', 'room']
    list_filter = ['hotel']


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    pass
