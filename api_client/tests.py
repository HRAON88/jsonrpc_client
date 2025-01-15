from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from jsonrpc.client import JsonRpcClient
from django.conf import settings
import json


class JsonRpcClientTests(TestCase):
    def setUp(self):
        self.client = JsonRpcClient('https://test.example.com/api/')

    @patch('http.client.HTTPSConnection')
    def test_successful_api_call(self, mock_https):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'result': {'_data': {'user': {'id': 1}}},
            'id': 1,
            'jsonrpc': '2.0'
        }).encode()
        mock_response.status = 200

        mock_connection = MagicMock()
        mock_connection.getresponse.return_value = mock_response
        mock_https.return_value = mock_connection

        response = self.client.call_method('auth.check', {})

        self.assertIn('result', response)
        self.assertEqual(response['result']['_data']['user']['id'], 1)
        mock_https.assert_called_once()
        mock_connection.request.assert_called_once()

    @patch('http.client.HTTPSConnection')
    def test_error_handling(self, mock_https):
        mock_https.side_effect = Exception('Connection error')
        response = self.client.call_method('auth.check', {})
        self.assertIn('error', response)
        self.assertEqual(response['error']['code'], -32603)
        self.assertEqual(response['error']['message'], 'Connection error')

    def test_create_temp_files(self):
        cert_file, key_file = self.client._create_temp_cert_files()
        try:
            self.assertTrue(open(cert_file).read())
            self.assertTrue(open(key_file).read())
        finally:
            self.client._cleanup_temp_files(cert_file, key_file)

    def test_certificate_loading(self):
        cert_file, key_file = self.client._create_temp_cert_files()
        try:
            with open(cert_file, 'r') as f:
                cert_content = f.read()
            with open(key_file, 'r') as f:
                key_content = f.read()
            self.assertIn('BEGIN CERTIFICATE', cert_content)
            self.assertIn('BEGIN PRIVATE KEY', key_content)
        finally:
            self.client._cleanup_temp_files(cert_file, key_file)


class ApiViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('api_view')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api_client/index.html')
        self.assertContains(response, 'auth.check')

    def test_post_invalid_json(self):
        response = self.client.post(self.url, {
            'method': 'auth.check',
            'params': '{invalid json}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid JSON format')

    @patch('jsonrpc.client.JsonRpcClient.call_method')
    def test_successful_post_request(self, mock_call_method):
        mock_call_method.return_value = {
            'result': {'_data': {'user': {'id': 1}}},
            'id': 1,
            'jsonrpc': '2.0'
        }

        response = self.client.post(self.url, {
            'method': 'auth.check',
            'params': '{}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user')
        mock_call_method.assert_called_once_with('auth.check', {})

    @patch('jsonrpc.client.JsonRpcClient.call_method')
    def test_error_response(self, mock_call_method):
        mock_call_method.return_value = {
            'error': {
                'code': -32603,
                'message': 'Test error'
            }
        }

        response = self.client.post(self.url, {
            'method': 'auth.check',
            'params': '{}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test error')


class FormTests(TestCase):
    def test_empty_params(self):
        response = Client().post(reverse('api_view'), {
            'method': 'auth.check',
            'params': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Invalid JSON format')

    def test_valid_json_params(self):
        response = Client().post(reverse('api_view'), {
            'method': 'auth.check',
            'params': '{"test": "value"}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Invalid JSON format')


class IntegrationTests(TestCase):
    def test_real_api_call(self):
        if not settings.CERT_DATA or not settings.KEY_DATA:
            self.skipTest("Certificates not configured")

        client = JsonRpcClient(settings.API_ENDPOINT)
        response = client.call_method('auth.check', {})

        self.assertNotIn('error', response)
        self.assertIn('result', response)
        self.assertIn('_data', response['result'])
        self.assertIn('user', response['result']['_data'])