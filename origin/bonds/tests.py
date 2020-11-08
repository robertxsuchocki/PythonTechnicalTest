import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from bonds.models import Bond


DEFAULT_USER_PARAMS = {'username': 'user', 'email': 'user@example.com', 'password': 'password'}


class ApplicationAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**DEFAULT_USER_PARAMS)
        self.login_path = '/auth/login/'
        self.bonds_path = '/bonds/'

    def test_needs_authentication(self):
        response = self.client.get(self.bonds_path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(self.bonds_path, {}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_success(self):
        response = self.client.post(self.login_path, data=DEFAULT_USER_PARAMS, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.bonds_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_success_without_username_or_email(self):
        for key in ['username', 'email']:
            params = dict(DEFAULT_USER_PARAMS)
            params.pop(key)
            response = self.client.post(self.login_path, params, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        params = dict(DEFAULT_USER_PARAMS)
        params['password'] = 'wrong'
        response = self.client.post(self.login_path, params, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        self.client.login(**DEFAULT_USER_PARAMS)
        response = self.client.post('/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.bonds_path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BondEndpointsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**DEFAULT_USER_PARAMS)
        self.bonds_path = '/bonds/'
        self.json = {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "R0MUWSFPU8MPRO8K5P83",
        }

    def test_bond_get_success(self):
        for _ in range(3):
            Bond.objects.create(**self.json, user=self.user, legal_name='')

        self.client.force_authenticate(self.user)
        response = self.client.get(self.bonds_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content)), Bond.objects.count())

    def test_bond_get_filter_own(self):
        other_user = User.objects.create_user(username='other_user', email='user2@example.com', password='password2')

        for _ in range(2):
            Bond.objects.create(**self.json, user=self.user, legal_name='')
        Bond.objects.create(**self.json, user=other_user, legal_name='')

        self.client.force_authenticate(self.user)
        response = self.client.get(self.bonds_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = len(json.loads(response.content))
        self.assertNotEqual(length, Bond.objects.count())
        self.assertEqual(length, Bond.objects.filter(user=self.user).count())

    @patch('bonds.viewsets.BondViewSet.get_legal_name_from_api')
    def test_bond_create_success(self, mock_instance):
        # API returned a correct value
        mock_instance.return_value = 'BNPPARIBAS'

        self.client.force_authenticate(self.user)
        response = self.client.post(self.bonds_path, json.dumps(self.json), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bond.objects.count(), 1)

    @patch('bonds.viewsets.BondViewSet.get_legal_name_from_api')
    def test_bond_create_no_legal_name(self, mock_instance):
        # get_legal_name_from_api returns None if API response is empty
        mock_instance.return_value = None

        self.client.force_authenticate(self.user)
        response = self.client.post(self.bonds_path, json.dumps(self.json), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bond.objects.count(), 0)


class BondModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**DEFAULT_USER_PARAMS)
        self.correct_data = {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "R0MUWSFPU8MPRO8K5P83",
            "user": self.user,
            "legal_name": "BNPPARIBAS",
        }

    def test_bond_isin_invalid(self):
        # checking special characters
        params = dict(self.correct_data, isin=",%@")
        bond = Bond(**params)
        self.assertRaises(ValidationError, bond.full_clean)

    def test_bond_currency_invalid(self):
        # checking for length, lower case letters, numbers, special characters
        values = ['GB', 'gbp', 'GB2', 'GB!']
        for value in values:
            params = dict(self.correct_data, currency=value)
            bond = Bond(**params)
            self.assertRaises(ValidationError, bond.full_clean)

    def test_bond_lei_invalid(self):
        # checking for length, lower case letters, special characters
        values = ['R0MUWS', 'r0muwsfpu8mpro8k5p83', '!0MUWSFPU8MPRO8K5P8#']
        for value in values:
            params = dict(self.correct_data, lei=value)
            bond = Bond(**params)
            self.assertRaises(ValidationError, bond.full_clean)
