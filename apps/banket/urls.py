from rest_framework.routers import DefaultRouter
from apps.banket.views import EventViewSet, DishViewSet, CommentViewSet, OrderedDishViewSet, HoleViewSet, GuestViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')
router.register(r'dishes', DishViewSet, basename='dishes')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'order', OrderedDishViewSet, basename='ordered-dishes')
router.register(r'hole', HoleViewSet, basename='hole')
router.register(r'guest', GuestViewSet, basename='guest')

urlpatterns = router.urls
