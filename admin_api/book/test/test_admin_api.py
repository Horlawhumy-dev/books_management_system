import pytest
from django.urls import reverse
from rest_framework import status
from book.test.factories import UserFactory,AdminBookFactory,AdminBook,User

from unittest.mock import patch, MagicMock
from django.db.models import F

pytestmark = pytest.mark.django_db
USER_LIST_URL = "book:user-list"
BOOK_LIST_URL = "book:adminbook-list"
BOOK_DETAIL_URL = "book:adminbook-detail"
USERS_WITH_BORROWED_BOOKS = "book:user-list-users-and-borrowed-books"
UNAVAILABLE_BOOK_WITH_RETRUN_DATE = "book:adminbook-list-borrowed-books-with-available-date"





class TestProductEndpoints:
    
    @patch('pika.BlockingConnection')
    @patch('pika.URLParameters')
    def test_create_book(self, mock_url_parameters, mock_blocking_connection, api_client, admin_book_data):
        """Test creation of book"""

        # Mock the RabbitMQ connection and channel
        
        mock_blocking_connection.return_value = MagicMock()
        mock_blocking_connection.return_value.channel.return_value = MagicMock()
        # Mock the basic_publish method
        mock_blocking_connection.return_value.channel.return_value.basic_publish.return_value = None

        payload = admin_book_data
        url = reverse(BOOK_LIST_URL)
        response = api_client.post(url, payload)
        assert response.status_code == 201


    def test_delete_book(self,api_client, admin_book_data):
        
        """Test deleting of a product"""
        book = AdminBookFactory()
        
        url = reverse(BOOK_DETAIL_URL, kwargs={"pk": book.id})
        response = api_client.delete(url)
        assert response.status_code == 204



    def test_list_users_in_library(self, api_client):

        UserFactory(email='user1@exa.org')
        UserFactory(email='abubakr@exa.org')
        UserFactory(email='sanusi@exa.org')

   
        url = reverse(USER_LIST_URL)
        response = api_client.get(url)
        print(response)
        assert response.status_code == 200
        assert response.json()["total"] == 3



    def test_list_users_with_books_borrowed_in_library(self, api_client):
        user1 = UserFactory(email='user1@exa.org')
        user2 =  UserFactory(email='abubakr@exa.org')
        user3 =  UserFactory(email='sanusi@exa.org')

        user1.refresh_from_db()
        user2.refresh_from_db()
        user3.refresh_from_db()
        
        AdminBookFactory.create_batch(2,borrowed_by=user1,is_available=False)
        AdminBookFactory.create_batch(3,borrowed_by=user1,is_available=True)
        AdminBookFactory.create_batch(2,borrowed_by=user2,is_available=False)
        AdminBookFactory.create_batch(2,borrowed_by=user3,is_available=False)
        
        url = reverse(USERS_WITH_BORROWED_BOOKS)
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()["total"] == 3

        
    def test_list_books_not_available_for_borrowing(self, api_client):
        user1 = UserFactory(email='user1@exa.org')
        user2 =  UserFactory(email='abubakr@exa.org')
        user3 =  UserFactory(email='sanusi@exa.org')

        user1.refresh_from_db()
        user2.refresh_from_db()
        user3.refresh_from_db()
        
        AdminBookFactory.create_batch(2,borrowed_by=user1,is_available=False,borrowed_until="2024-09-14T19:44:29.799865Z")
        AdminBookFactory.create_batch(2,borrowed_by=user1,is_available=False)
        AdminBookFactory.create_batch(3,borrowed_by=user1,is_available=True)
        AdminBookFactory.create_batch(2,borrowed_by=user2,is_available=False,borrowed_until="2024-09-14T19:44:29.799865Z")
        AdminBookFactory.create_batch(2,borrowed_by=user3,is_available=True)
        
        url = reverse(UNAVAILABLE_BOOK_WITH_RETRUN_DATE)
        response = api_client.get(url)
        print(response.json())
        assert response.status_code == 200
        assert response.json()['total'] == 4



  