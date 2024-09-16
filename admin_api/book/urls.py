from django.urls import path, include
from .views import UserViewSet,AdminBookViewSet
from rest_framework import routers

app_name = "book"
router = routers.DefaultRouter()

router.register("users", viewset=UserViewSet)
router.register("books", viewset=AdminBookViewSet)

urlpatterns = [path("", include(router.urls))]
