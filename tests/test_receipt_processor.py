import unittest
from unittest.mock import patch, MagicMock
import uuid
import math
from datetime import datetime
from models import Receipt, Item
import logging
from receipt_processor import generate_id, from_json_to_receipt, calculate_points, count_rule_retailer_name, count_rule_receipt_total, count_rule_receipt_items, count_rule_receipt_datetime

class TestReceiptProcessor(unittest.TestCase):

    @patch("uuid.uuid3")
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
    
    @patch("receipt_processor.count_rule_retailer_name")
    @patch("receipt_processor.count_rule_receipt_total")
    @patch("receipt_processor.count_rule_receipt_items")
    @patch("receipt_processor.count_rule_receipt_datetime")
    def test_calculate_points(self, mock_datetime, mock_items, mock_total, mock_retailer):
        # Test that calculate_points returns the expected total points based on the individual rules
        
        receipt_json = '{"retailer": "Store A", "purchaseDate": "2022-04-01", "purchaseTime": "14:33", "items": [{"shortDescription": "item1", "price": 5.99}], "total": 5.99}'
        
        receipt = from_json_to_receipt(receipt_json)
        
        # Mock each rule to return fixed points
        mock_retailer.return_value = 10
        mock_total.return_value = 50
        mock_items.return_value = 25
        mock_datetime.return_value = 15
        
        total_points = calculate_points(receipt_json)
        
        self.assertEqual(total_points, 100)  # 10 + 50 + 25 + 15
    
    def test_count_rule_retailer_name(self):
        # Test the retailer name points rule
        
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        points = count_rule_retailer_name(receipt)
        
        self.assertEqual(points, 9)  # 'Store A' has 9 alphanumeric characters
    
    def test_count_rule_receipt_total(self):
        # Test the receipt total points rule
        
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.00)
        points = count_rule_receipt_total(receipt)
        
        self.assertEqual(points, 50)  # 50 points for a round dollar amount
        
        receipt.total = 5.25
        points = count_rule_receipt_total(receipt)
        self.assertEqual(points, 75)  # 50 for round dollars + 25 for multiple of 0.25
    
    def test_count_rule_receipt_items(self):
        # Test the receipt items points rule
        
        item1 = Item(shortDescription="item1", price=5.99)
        item2 = Item(shortDescription="item2", price=3.99)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[item1, item2], total=5.99)
        
        points = count_rule_receipt_items(receipt)
        
        self.assertEqual(points, 10)  # 5 points for every 2 items, plus 0 for descriptions
        
        # Test with description length multiple of 3
        item3 = Item(shortDescription="item333", price=7.99)
        receipt.items.append(item3)
        
        points = count_rule_receipt_items(receipt)
        
        self.assertEqual(points, 14)  # 10 from item count, 4 from item3 (7.99 * 0.2 rounded up)
    
    def test_count_rule_receipt_datetime(self):
        # Test the receipt datetime points rule
        
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 1), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        
        points = count_rule_receipt_datetime(receipt)
        
        self.assertEqual(points, 10)  # Time between 2:00 PM and 4:00 PM
        
        # Test for odd day purchase date
        receipt.purchaseDate = datetime(2022, 4, 3)  # Odd day
        points = count_rule_receipt_datetime(receipt)
        
        self.assertEqual(points, 16)  # 6 points for odd day + 10 for time
    
    def test_count_rule_receipt_datetime_even_day(self):
        # Test for even day (no points for odd day rule)
        receipt = Receipt(retailer="Store A", purchaseDate=datetime(2022, 4, 2), purchaseTime="14:33", items=[Item(shortDescription="item1", price=5.99)], total=5.99)
        
        points = count_rule_receipt_datetime(receipt)
        
        self.assertEqual(points, 10)  # Only time points, no points for the odd day rule


if __name__ == "__main__":
    unittest.main()
