import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_book_data():
    return {
        'title': 'Test Book',
        'author': 'Author Name',
        'publisher': 'Publisher Name',
        'category': 'Category'
    }

@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
    }



