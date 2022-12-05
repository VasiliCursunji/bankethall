from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum, F
from django.template.loader import get_template
from django_filters.rest_framework import DjangoFilterBackend
from django.template import Context
from rest_framework import viewsets, status, views
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.banket.helpers import get_weekday_name
from apps.banket.models import Event, Dish, Comment, OrderedDish, Hole, Guest, Seat, AdditionalOptions
from apps.banket.permissions import IsOwnerOrReadOnly
from apps.banket.serializers import EventSerializer, DishSerializer, CommentSerializer, OrderedDishSerializer, \
    HoleSerializer, GuestSerializer, SeatChangeSerializer, AdditionalOptionsSerializer, \
    AdditionalOptionsChangeSerializer, EventDetailSerializer, InvitationSerializer, EventListSerializer, SeatSerializer

from config.settings import EMAIL_HOST_USER


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filter_fields = (
        'event_type',
        'is_passed',
    )
    search_fields = (
        'description',
    )
    ordering_fields = (
        'id',
    )

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user, hole_id=1)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EventDetailSerializer(instance)
        if instance.user == self.request.user:
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data='Вы не можете просматривать чужие мероприятия', status=status.HTTP_403_FORBIDDEN)

    @action(methods=['GET'], detail=False, serializer_class=EventListSerializer, url_path='my-events')
    def my_events(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=Serializer, url_path='event-seats')
    def event_seats(self, request, *args, **kwargs):
        queryset = Seat.objects.filter(event_id=kwargs['pk']).order_by('id')
        serializer = SeatSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=Serializer, url_path='event-guests')
    def event_guests(self, request, *args, **kwargs):
        queryset = Guest.objects.filter(event_id=kwargs['pk']).order_by('id')
        serializer = GuestSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=Serializer, url_path='total-price')
    def total_price(self, request, *args, **kwargs):
        instance = self.get_object()
        dishes_price = OrderedDish.objects.filter(
            user=self.request.user,
            event=instance
        ).aggregate(
            total=Sum(F('amount') * F('dish__price'))
        )['total']
        options_price = instance.get_options_price
        if not dishes_price:
            return Response(data={"price": options_price}, status=status.HTTP_200_OK)
        return Response(data={"price": dishes_price + options_price}, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=True, serializer_class=AdditionalOptionsChangeSerializer, url_path='add-options')
    def add_options(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.add_options.add(*request.data['add_options'])
        instance.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=True, serializer_class=AdditionalOptionsChangeSerializer,
            url_path='delete-options')
    def delete_options(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.add_options.remove(*request.data['add_options'])
        instance.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, serializer_class=Serializer, url_path='all-options')
    def all_options(self, request, *args, **kwargs):
        options = AdditionalOptions.objects.values()
        return Response(data=options, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=InvitationSerializer, url_path='send-invitations')
    def send_invitations(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        wedding = {
            'women': {
                'name': data['women_fullname'].split()[0],
                'fullname': data['women_fullname']
            },
            'man': {
                'name': data['man_fullname'].split()[0],
                'fullname': data['man_fullname']
            },
            'label': data['women_fullname'][0] + '&' + data['man_fullname'][0],
            'day': get_weekday_name(instance.date_planned.weekday()),
            'date': instance.date_planned.strftime("%m/%d"),
            'year': instance.date_planned.strftime("%Y")
        }

        htmly = get_template('Save the date.html')
        d = {'wedding': wedding}
        html_content = htmly.render(d)

        email_guests = list(Guest.objects.filter(event=instance).values_list('email'))
        email_guests = [i[0] for i in email_guests]

        subject, from_email, to = 'Wedding invitation', EMAIL_HOST_USER, email_guests
        text_content = 'You are invited to our weeding!'
        mail = EmailMultiAlternatives(subject, text_content, from_email, to)

        mail.attach_alternative(html_content, "text/html")
        mail.send()

        return Response(status=status.HTTP_200_OK)


class DishViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = DishSerializer
    queryset = Dish.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(
    viewsets.GenericViewSet,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin
):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class OrderedDishViewSet(
    viewsets.GenericViewSet,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = OrderedDishSerializer
    queryset = OrderedDish.objects.all()

    @action(methods=['GET'], detail=False, serializer_class=OrderedDishSerializer, url_path='my-ordered-dishes')
    def my_ordered_dishes(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class HoleViewSet(
    viewsets.GenericViewSet,
    RetrieveModelMixin,
    ListModelMixin,
):
    permission_classes = (AllowAny,)
    serializer_class = HoleSerializer
    queryset = Hole.objects.all()


class GuestViewSet(
    viewsets.GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = GuestSerializer
    queryset = Guest.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        seat = Seat.objects.filter(number=self.request.data['seat'], event_id=self.request.data['event']).first()
        seat.take_the_place()
        serializer.save(user=user, seat=seat)

    @action(methods=['POST'], detail=True, serializer_class=SeatChangeSerializer, url_path='change-seat')
    def change_seat(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_seat = Seat.objects.filter(number=self.request.data['seat_number'],
                                       event_id=self.request.data['event_id']).first()
        serializer.save(seat_id=new_seat)
        new_seat.take_the_place()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=Serializer, url_path='make-seat-free')
    def make_seat_free(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.seat_free()

        return Response(data={'Seat is free'}, status=status.HTTP_200_OK)
