import factory
from book.models import User,AdminBook


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class AdminBookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AdminBook
    