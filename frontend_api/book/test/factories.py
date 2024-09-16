import factory
from book.models import User,Book


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book
    