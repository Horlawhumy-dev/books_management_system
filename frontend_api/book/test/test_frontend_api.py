import pytest
from django.urls import reverse
from rest_framework import status
from book.test.factories import UserFactory,BookFactory

from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.django_db
USER_LIST_URL = "book:user-list"
BOOK_LIST_URL = "book:book-list"
BOOK_DETAIL_URL = "book:book-detail"
BORROW_URL = "book:book-borrow"




class TestProductEndpoints:
    
    @patch('pika.BlockingConnection')
    @patch('pika.URLParameters')
    def test_create_user(self, mock_url_parameters, mock_blocking_connection, api_client, user_data):
        """Test creation of user"""

        # Mock the RabbitMQ connection and channel
        
        mock_blocking_connection.return_value = MagicMock()
        mock_blocking_connection.return_value.channel.return_value = MagicMock()
        # Mock the basic_publish method
        mock_blocking_connection.return_value.channel.return_value.basic_publish.return_value = None

        payload = user_data
        url = reverse(USER_LIST_URL)
        response = api_client.post(url, payload)
        assert response.status_code == 201

    

    def test_list_available_books(self, api_client):

        BookFactory.create_batch(3,is_available=True)
        BookFactory.create_batch(2,is_available=False)
        
        url = reverse(BOOK_LIST_URL)
        response = api_client.get(url)
        print(response)
        assert response.status_code == 200
        assert response.json()["total"] == 3


    def test_get_book(self, api_client):
        """Test getting of a book"""
        book = BookFactory(is_available=True)
        url = reverse(BOOK_DETAIL_URL, kwargs={"pk": book.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["title"] == book.title
        assert response.data["author"] == book.author



    def test_filter_books_by_publisher(self, api_client):

        BookFactory.create_batch(3,is_available=True,publisher='Mark Dan')
        BookFactory.create_batch(2,is_available=True,publisher='James')
        BookFactory.create_batch(2,is_available=False)
        
        url = reverse(BOOK_LIST_URL)
        publisher="James"
        joined_url = url + f"?publisher={publisher}"
        response = api_client.get(joined_url,format="json")
        assert response.status_code == 200
        assert response.json()["total"] == 2
    

    def test_filter_books_by_category(self, api_client):

        BookFactory.create_batch(3,is_available=True,category='Mark Dan')
        BookFactory.create_batch(2,is_available=True,category='James')
        BookFactory.create_batch(2,is_available=False)
        
        url = reverse(BOOK_LIST_URL)
        category="James"
        joined_url = url + f"?category={category}"
        response = api_client.get(joined_url,format="json")
        assert response.status_code == 200
        assert response.json()["total"] == 2


    def test_update_product(self, api_client,user_data):
        print(user_data)
        book = BookFactory(is_available=True)

        payload = {
        "user_email": user_data["email"],
        "days_to_be_used":7
        
         }
        url = reverse(BORROW_URL, kwargs={"pk": book.id})
        response = api_client.post(url, payload)
       
       
        book.refresh_from_db()

        assert response.status_code == 200
        assert book.borrowed_by != None
        assert book.is_available ==False
        assert book.borrowed_until != None
 
        