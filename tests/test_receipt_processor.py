import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

from app.receipt_processor import generate_id, from_json_to_receipt, calculate_points, count_rule_retailer_name, count_rule_receipt_total, count_rule_receipt_items, count_rule_receipt_datetime
from app.models import Receipt, Item

class TestReceiptProcessor(unittest.TestCase):

    @patch("app.receipt_processor.uuid.uuid3")
    def test_generate_id(self, mock_uuid3):
        # Test that the generate_id function generates the expected UUID based on the receipt string
        receipt_string = "test_receipt_data"
        expected_uuid = uuid.uuid4()  # Use a mock UUID for testing
        mock_uuid3.return_value = expected_uuid
        
        result = generate_id(receipt_string)
        self.assertEqual(result, expected_uuid)
        mock_uuid3.assert_called_once_with(uuid.NAMESPACE_DNS, receipt_string)

    def test_from_json_to_receipt_valid(self):
        # Test that from_json_to_receipt correctly parses a valid JSON string into a Receipt object
        receipt_json = '{"retailer": "Store A", "purchaseDate": "2022-04-01", "purchaseTime": "14:33", "items": [{"shortDescription": "item1", "price": 5.99}], "total": 5.99}'
        
        receipt = from_json_to_receipt(receipt_json)
        
        self.assertIsInstance(receipt, Receipt)
        self.assertEqual(receipt.retailer, "Store A")
        self.assertEqual(receipt.total, 5.99)
        self.assertEqual(len(receipt.items), 1)

    def test_from_json_to_receipt_invalid(self):
        # Test that from_json_to_receipt raises an error for invalid JSON
        invalid_receipt_json = '{"retailer": "Store A", "total": 5.99'
        
        with self.assertRaises(Exception):
            from_json_to_receipt(invalid_receipt_json)

    def test_calculate_points_retailer_name(self):
        # Test the retailer name points rule
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        
        points = count_rule_retailer_name(receipt)
        
        self.assertEqual(points, 6)  # 'Store A' has 6 alphanumeric characters

    def test_calculate_points_round_dollar_total(self):
        # Test for round dollar total (50 points)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.00)
        
        points = count_rule_receipt_total(receipt)
        
        self.assertEqual(points, 75)  # 50 points for a round dollar amount, 25 for multiple of 0.25

    def test_calculate_points_multiple_of_0_25_total(self):
        # Test for total that is a multiple of 0.25 (25 points)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.25)
        
        points = count_rule_receipt_total(receipt)
        
        self.assertEqual(points, 25)  # 25 for multiple of 0.25

    def test_calculate_points_items_count(self):
        # Test for item count (5 points for every two items)
        item1 = Item(shortDescription="item1", price=5.99)
        item2 = Item(shortDescription="item2", price=3.99)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[item1, item2], total=5.99)
        
        points = count_rule_receipt_items(receipt)
        
        self.assertEqual(points, 5)  # 5 points for every 2 items



    def test_calculate_points_purchase_after_2pm(self):
        # Test for purchase time between 2:00 PM and 4:00 PM (10 points)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        
        points = count_rule_receipt_datetime(receipt)
        
        self.assertEqual(points, 16)  # 6 points for odd day, 10 points for time between 2 PM and 4 PM

    def test_calculate_points_purchase_odd_day(self):
        # Test for purchase on an odd day (6 points)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 3), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        
        points = count_rule_receipt_datetime(receipt)
        
        self.assertEqual(points, 16)  # 6 points for odd day + 10 for time

    def test_calculate_points_purchase_even_day(self):
        # Test for purchase on an even day (no points for odd day rule)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 2), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        
        points = count_rule_receipt_datetime(receipt)
        
        self.assertEqual(points, 10)  # Only time points, no points for the odd day rule

if __name__ == "__main__":
    unittest.main()
