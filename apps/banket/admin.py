from django.contrib import admin
from apps.banket.models import Event, Hole, Image, Dish, OrderedDish, Comment, Seat, AdditionalOptions


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Hole)
class HoleAdmin(admin.ModelAdmin):
    inlines = [ImageInline, ]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderedDish)
class OrderedDishAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class DishAdmin(admin.ModelAdmin):
    pass


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    pass


@admin.register(AdditionalOptions)
class AdditionalOptionsAdmin(admin.ModelAdmin):
    pass
