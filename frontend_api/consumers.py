import pika
import json
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  
django.setup()


from django.conf import settings

from book.models import User,Book


def process_book_updates(ch, method, properties, body):
    data = json.loads(body)
    event_type = data['event_type']
    book_data = data['book_data']

    try:
        if event_type == 'add':
            Book.objects.create(
                external_id=book_data['external_id'],
                title=book_data['title'],
                author=book_data['author'],
                publisher=book_data['publisher'],
                category=book_data['category'],
                is_available=book_data['is_available'],
            )
        elif event_type == 'update':
            book = Book.objects.get(external_id=book_data['external_id'])
            book.title = book_data['title']
            book.author = book_data['author']
            book.publisher = book_data['publisher']
            book.category = book_data['category']
            book.is_available = book_data['is_available']
            book.save()
        elif event_type == 'delete':
            Book.objects.filter(external_id=book_data['external_id']).delete()
    except Book.DoesNotExist:
        pass

def start_book_update_consumer():
    
    parameters = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='book_updates', durable=True)
    channel.basic_consume(queue='book_updates', on_message_callback=process_book_updates, auto_ack=True)
    channel.start_consuming()



if __name__ == '__main__':
    start_book_update_consumer()
