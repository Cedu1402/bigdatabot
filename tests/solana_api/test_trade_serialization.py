import json
import unittest
from datetime import datetime

from solana_api.trade_model import Trade


class TestRunner(unittest.TestCase):

    def test_trade_serialization(self):

        trade = Trade("test", "testpump", 100, 1, True, 10, "2")
        try:
            json.dumps(trade.to_dict())
        except TypeError as e:
            self.fail("TypeError was raised during serialization")

    def test_trade_deserialization(self):
        # Original Trade object
        trade = Trade("test", "testpump", 100, 1, True, 10, "2024-12-06T12:00:00")

        # Serialize the object
        trade_dict = trade.to_dict()
        trade_json = json.dumps(trade_dict)

        try:
            # Deserialize the JSON string back into a dictionary
            trade_data = json.loads(trade_json)

            # Recreate a Trade object from the dictionary
            deserialized_trade = Trade(**trade_data)

            # Check if deserialized data is equivalent to the original
            self.assertEqual(trade, deserialized_trade)
            self.assertIsInstance(trade.get_time(), datetime)
        except (TypeError, json.JSONDecodeError) as e:
            self.fail(f"Deserialization failed: {e}")
