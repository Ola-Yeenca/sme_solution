import unittest
import json
import os
import logging

# Adjust the import path to locate your app module
from api.app import app

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.app = app
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertIn('time', data)

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # optionally check that the index.html content is served appropriately
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_invalid_route(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'error')

    def test_analyze_endpoint_missing_data(self):
        response = self.client.post('/api/v1/analyze/pricing', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'error')

    def test_analyze_endpoint_valid_data(self):
        # Use valid real-world-like input
        payload = {
            "business_name": "Test Business",
            "business_type": "restaurant"
        }
        response = self.client.post('/api/v1/analyze/pricing', data=json.dumps(payload), content_type='application/json')
        # The analyzer may return 200 or, if using real external APIs, could return rate limiting 429
        self.assertIn(response.status_code, [200, 429])
        if response.status_code == 200:
            data = response.get_json()
            self.assertEqual(data.get('status'), 'success')
            self.assertIn('data', data)
        elif response.status_code == 429:
            data = response.get_json()
            self.assertEqual(data.get('error'), 'Rate limit exceeded')

if __name__ == '__main__':
    # Use a higher verbosity for thorough test output
    unittest.main(verbosity=2)
