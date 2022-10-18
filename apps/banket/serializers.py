from rest_framework import serializers

from apps.banket.models import Event, Dish, Comment, OrderedDish, Hole, Image, Guest, Seat, AdditionalOptions
from apps.users.serializers import UserSerializer


class AdditionalOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalOptions
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id',
            'hole',
            'description',
            'event_type',
            'date_planned',
            'is_passed',
        )


class EventDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    add_options = AdditionalOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            'id',
            'user',
            'hole',
            'description',
            'event_type',
            'add_options',
            'date_created',
            'date_planned',
            'is_passed',
        )
        extra_kwargs = {
            'user': {'read_only': True},
            'date_created': {'read_only': True},
            'add_options': {'read_only': True},
        }


class AdditionalOptionsChangeSerializer(serializers.ModelSerializer):
    add_options = serializers.PrimaryKeyRelatedField(
        queryset=AdditionalOptions.objects.all(),
        required=True,
        many=True,
    )

    class Meta:
        model = Event
        fields = (
            'add_options',
        )


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'text'
        )

    extra_kwargs = {
        'user': {'read_only': True}
    }


class OrderedDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer()
    event = EventSerializer()

    class Meta:
        model = OrderedDish
        fields = (
            'id',
            'dish',
            'amount',
            'event',
        )


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            'id',
            'image',
        )


class HoleSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Hole
        fields = (
            'id',
            'name',
            'description',
            'number_of_seats',
            'images',
        )


class GuestSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True)
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    user = UserSerializer(read_only=True)

    class Meta:
        model = Guest
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'seat',
            'event',
            'user',
        )

        extra_kwargs = {
            'user': {'read_only': True},
            'event': {'write_only': True},
        }


class SeatChangeSerializer(serializers.ModelSerializer):
    seat_id = serializers.IntegerField(required=True)

    class Meta:
        model = Guest
        fields = (
            'seat_id',
        )
