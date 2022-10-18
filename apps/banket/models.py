from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Dish(models.Model):
    DISH_TYPES = (
        ('COLD', 'Cold'),
        ('WARM', 'Warm'),
        ('SNACK', 'Snack'),
        ('SALAD', 'Salad'),
        ('DRINK', 'Drink'),
    )

    name = models.CharField(max_length=255)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    description = models.TextField(default='Dish')
    dish_type = models.CharField(max_length=255, choices=DISH_TYPES)


class Hole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default='Hole')
    number_of_seats = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Image(models.Model):
    hole = models.ForeignKey(Hole, related_name='images', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='media/')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()


class Event(models.Model):
    EVENT_TYPES = (
        ('BIRTHDAY', 'Birthday'),
        ('WEDDING', 'Wedding'),
        ('CHRISTENING', 'Сhristening'),
        ('OTHER', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE, null=True)
    description = models.TextField(default='My Event')
    event_type = models.CharField(max_length=255, choices=EVENT_TYPES)
    date_created = models.DateTimeField(auto_now_add=True)
    date_planned = models.DateField(null=True)
    is_passed = models.BooleanField(default=False)


class OrderedDish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    @property
    def calculate_price(self):
        return self.dish.price * self.amount


# Когда создается новое мероприятие, создаются места для него ( столько сколько есть в зале ). Можно через сигналы
class Seat(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    description = models.TextField(default='')
    is_engaged = models.BooleanField(default=False)

    def take_the_place(self):
        self.is_engaged = True
        self.save()


class Guest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    seat = models.ForeignKey(Seat, related_name='seat', on_delete=models.CASCADE, null=True)
    event = models.ForeignKey(Event, related_name='event', on_delete=models.CASCADE, null=True)

    def seat_free(self):
        self.seat = None
        self.save()


@receiver(post_save, sender=Event)
def create_seats(sender, instance, created, **kwargs):
    if created:
        Seat.objects.bulk_create(
            [Seat(
                event=instance,
                number=i
            ) for i in range(1, instance.hole.number_of_seats + 1)]
        )
