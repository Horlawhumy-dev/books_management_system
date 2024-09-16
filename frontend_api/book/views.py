from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.permissions import AllowAny
import json
import pika


from .models import Book, User
from .serializers import BookSerializer, BorrowerSerializer, UserSerializer
from django.conf import settings

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post", "patch", "put", "delete","get"]
    

    def sync_with_admin(self, data, event_type):
        parameters = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='user_updates', durable=True)
        
        event = {
            'event_type': event_type,
            'user_data': {
                'external_id': data['id'],
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
            }
        }
        channel.basic_publish(exchange='', routing_key='user_updates', body=json.dumps(event))
        connection.close()

    def perform_create(self, serializer):
        serializer.save()
        self.sync_with_admin(serializer.data, 'add')

    def perform_update(self, serializer):
        serializer.save()
        self.sync_with_admin(serializer.data, 'update')


    def perform_destroy(self, instance):
        data = UserSerializer(instance).data
        self.sync_with_admin(data, 'delete')
        instance.delete()

    



class BookViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Book.objects.filter(is_available=True).select_related('borrowed_by').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publisher', 'category']
    search_fields = ['author', 'publisher', 'category']
    ordering_fields = ['updated_at']
    permission_classes = [AllowAny]

    def sync_with_admin(self, data, event_type):
        parameters = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='borrow_updates', durable=True)
        
        event = {
            'event_type': event_type,
            'book_data': {
                'external_id': data['external_id'],
                'title': data['title'],
                'author': data['author'],
                'publisher': data['publisher'],
                'category': data['category'],
                'borrowed_by': str(data['borrowed_by']) if data['borrowed_by'] else None,
                'borrowed_until': str(data['borrowed_until']) if data['borrowed_until'] else None,
                'is_available': data['is_available'],
            }
        }
        channel.basic_publish(exchange='', routing_key='borrow_updates', body=json.dumps(event))
        connection.close()

    @action(detail=True, methods=['post'], serializer_class=BorrowerSerializer)
    def borrow(self, request, pk=None):
        book = self.get_object()

        serializer = BorrowerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data["user_email"]
        days = int(serializer.validated_data["days_to_be_used"])

        user, _ = User.objects.get_or_create(email=user_email)
        book.borrowed_by = user
        end_date = timezone.now() + timezone.timedelta(days=days)
        book.borrowed_until =end_date
        book.is_available = False
        book.save()

        # Sync with RabbitMQ after borrowing
        self.sync_with_admin(BookSerializer(book).data, 'borrow')

        response = {
            "message": "Book borrowed successfully",
            **BookSerializer(instance=book).data,
        }
        return Response(data=response, status=status.HTTP_200_OK)
