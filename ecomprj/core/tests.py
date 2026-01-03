from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class AddressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_address(self):
        url = "/api/addresses/"
        data = {
            "address_type": "shipping",
            "full_name": "John Doe",
            "phone": "1234567890",
            "address_line_1": "123 Main St",
            "city": "Test City",
            "state": "Test State",
            "country": "Test Country",
            "zip_code": "12345"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_addresses(self):
        Address.objects.create(user=self.user, full_name="John Doe", address_line_1="123 Main St", city="Test City", state="Test State", country="Test Country", zip_code="12345")
        url = "/api/addresses/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

# Create your tests here.
