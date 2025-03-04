import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import json
from app.main import app  # Assuming your FastAPI app is in 'main.py'

class TestFastAPIApp(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
    
    @patch("app.main.generate_id")
    @patch("app.main.calculate_points")
    @patch("app.main.store_receipt")
    def test_submit_receipt_success(self, mock_store_receipt, mock_calculate_points, mock_generate_id):
        # Test data
        payload = {
            "retailer": "Store A",
            "purchaseDate": "2022-04-01",
            "purchaseTime": "14:33",
            "items": [{"shortDescription": "item1", "price": 5.99}],
            "total": 5.99
        }
        
        receipt_id = "generated-uuid"
        points = 100
        
        # Mock the dependencies
        mock_generate_id.return_value = receipt_id
        mock_calculate_points.return_value = points
        mock_store_receipt.return_value = True  # Simulate success in DB insertion
        
        # Make a POST request to the /receipts/process endpoint
        response = self.client.post("/receipts/process", json=payload)
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": receipt_id})
        
        mock_generate_id.assert_called_once_with(json.dumps(payload))
        mock_calculate_points.assert_called_once_with(json.dumps(payload))
        mock_store_receipt.assert_called_once_with(receipt_id, points, payload)

    @patch("app.main.store_receipt")
    def test_submit_receipt_failure_db_error(self, mock_store_receipt):
        # Test data
        payload = {
            "retailer": "Store B",
            "purchaseDate": "2022-04-01",
            "purchaseTime": "14:33",
            "items": [{"shortDescription": "item1", "price": 5.99}],
            "total": 5.99
        }
        
        # Mock store_receipt to simulate a DB failure
        mock_store_receipt.return_value = None  # Simulate failure in DB insertion
        
        # Make a POST request to the /receipts/process endpoint
        response = self.client.post("/receipts/process", json=payload)
        print("Shariah", response)
        # Validate the response
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Error processing receipt."})

    @patch("app.main.get_receipt_points")
    def test_get_receipt_points_success(self, mock_get_receipt_points):
        receipt_id = "a44f6c64-4d6a-3a9e-9c84-9193edc11dc8"
        points = 22
        
        # Mock get_receipt_points to return the expected points
        mock_get_receipt_points.return_value = [points]
        
        # Make a GET request to the /receipts/{receipt_id}/points endpoint
        response = self.client.get(f"/receipts/{receipt_id}/points")
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"points": points})
        
        mock_get_receipt_points.assert_called_once_with(receipt_id)

    @patch("app.main.get_receipt_points")
    def test_get_receipt_points_not_found(self, mock_get_receipt_points):
        receipt_id = "non-existent-receipt-id"
        
        # Mock get_receipt_points to return None (simulate not found)
        mock_get_receipt_points.return_value = None
        
        # Make a GET request to the /receipts/{receipt_id}/points endpoint
        response = self.client.get(f"/receipts/{receipt_id}/points")
        print("Shariah23" , response)
        # Validate the response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "No receipt found for that ID."})
        
        mock_get_receipt_points.assert_called_once_with(receipt_id)

    def test_health_check(self):
        # Make a GET request to the /health endpoint
        response = self.client.get("/health")
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

if __name__ == '__main__':
    unittest.main()
