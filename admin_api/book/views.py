from rest_framework import viewsets,mixins
from .models import AdminBook, User
from .serializers import AdminBookSerializer,AdminCreateBookSerializer, UnavailableBooksSerializer, UserSerializer, UsersAndBorrowedBooksSerializer
import json
import pika
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Prefetch

class AdminBookViewSet(viewsets.ModelViewSet):
    queryset = AdminBook.objects.all()
    serializer_class = AdminBookSerializer
    permission_classes = [AllowAny]

    def sync_with_frontend(self, data, event_type):
        parameters = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='book_updates', durable=True)
        event = {
            'event_type': event_type,
            'book_data': {
                'external_id': data['id'],
                'title': data['title'],
                'author': data['author'],
                'publisher': data['publisher'],
                'category': data['category'],
                'is_available': data['is_available'],
            }
        }
        channel.basic_publish(exchange='', routing_key='book_updates', body=json.dumps(event))
        connection.close()


    def get_serializer_class(self):
        if self.action in ["create","partial_update","update"]:
            return AdminCreateBookSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save()
        self.sync_with_frontend(serializer.data, 'add')

    def perform_update(self, serializer):
        serializer.save()
        self.sync_with_frontend(serializer.data, 'update')

    def perform_destroy(self, instance):
        data = AdminBookSerializer(instance).data
        self.sync_with_frontend(data, 'delete')
        instance.delete()


    def paginate_results(self, queryset, serializer=None):
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer if not serializer else serializer
        if page is not None:
            serializer = serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=UnavailableBooksSerializer,
        permission_classes=[AllowAny],
        url_path='list-borrowed-books-with-available-date',
    )

    def list_borrowed_books_with_available_date(self,request,pk=None):
        qs = self.get_queryset().exclude(is_available=True).filter(borrowed_until__isnull=False).all()
        
        return self.paginate_results(qs,UnavailableBooksSerializer)


    
class UserViewSet( mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    """Already contains list and get endpoints for users"""
    queryset = User.objects.prefetch_related('books').all()
   

    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def paginate_results(self, queryset, serializer=None):
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer if not serializer else serializer
        if page is not None:
            serializer = serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=UsersAndBorrowedBooksSerializer,
        permission_classes=[AllowAny],
        url_path='list-users-and-borrowed-books',
    )

    def list_users_and_borrowed_books(self, request):
        users = self.get_queryset()
        qs = [{"user": user, "books_borrowed": user.books.all()} for user in users]

        return self.paginate_results(qs,UsersAndBorrowedBooksSerializer)
        
        
        
            

        
     


    
    

    






   
    


    
    

    

    
