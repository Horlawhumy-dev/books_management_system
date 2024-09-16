import pika
import json
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  
django.setup()

from django.conf import settings
from django.utils.dateparse import parse_date

from book.models import AdminBook,User

print(settings.RABBITMQ_URL)


def process_borrowed_updates(ch, method, properties, body):
    data = json.loads(body)
    event_type = data['event_type']
    book_data = data['book_data']

    try:
        if event_type == 'borrow':
           
            book = AdminBook.objects.get(id=book_data['external_id'])
            book.title = book_data['title']
            book.author = book_data['author']
            book.publisher = book_data['publisher']
            book.category = book_data['category']
            book.is_available = book_data['is_available']
            
            book.borrowed_by,_ = User.objects.get_or_create(external_id=book_data['borrowed_by'])
            
            book.borrowed_until = (book_data['borrowed_until'])
            book.save()
        
    except AdminBook.DoesNotExist:
        pass
    except User.DoesNotExist:
        pass


def process_user_updates(ch, method, properties, body):
    data = json.loads(body)
    event_type = data['event_type']
    user_data = data['user_data']

    try:
        if event_type == 'add':
            User.objects.create(
                external_id=user_data['external_id'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
            )
        elif event_type == 'update':
            user = User.objects.get(external_id=user_data['external_id'])
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.save()
        elif event_type == 'delete':
            User.objects.filter(external_id=user_data['external_id']).delete()
    except User.DoesNotExist:
        pass


def start_user_update_consumer():
    parameters = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declaring the user_updates queue
    channel.queue_declare(queue='user_updates', durable=True)
    channel.basic_consume(queue='user_updates', on_message_callback=process_user_updates, auto_ack=True)
    
    # Declaring the book_updates queue
    channel.queue_declare(queue='borrow_updates', durable=True)
    channel.basic_consume(queue='borrow_updates', on_message_callback=process_borrowed_updates, auto_ack=True)
    
    # Start consuming messages from the queues
    channel.start_consuming()


if __name__ == '__main__':
    start_user_update_consumer()
