import json
import unittest

from bot.event_worker import get_trader_form_event


class TestGetTraderFromEvent(unittest.TestCase):

    def setUp(self):
        self.event = json.dumps({
            "jsonrpc": "2.0",
            "method": "accountNotification",
            "params": {
                "result": {
                    "context": {"slot": 5199307},
                    "value": {
                        "data": [
                            "11116bv5nS2h3y12kD1yUKeMZvGcKLSjQgX6BeV7u1FrjeJcKfsHPXHRDEHrBesJhZyqnnq9qJeUuF7WHxiuLuL5twc38w2TXNLxnDbjmuR",
                            "base58"
                        ],
                        "executable": False,
                        "lamports": 33594,
                        "owner": "11111111111111111111111111111111",
                        "rentEpoch": 635,
                        "space": 80
                    }
                },
                "subscription": 23784
            }
        })

    def test_get_trader_from_event_found(self):
        # Define the mock event and subscription map
        subscription_map = {
            23784: "Trader_ABC123"  # Trader associated with subscription ID 23784
        }

        # Call the method
        trader = get_trader_form_event(self.event, subscription_map)

        # Verify that the correct trader is returned
        self.assertEqual(trader, "Trader_ABC123")

    def test_get_trader_from_event_not_found(self):
        subscription_map = {}  # Empty map, subscription ID will not be found

        # Call the method
        trader = get_trader_form_event(self.event, subscription_map)

        # Verify that None is returned and an error is logged
        self.assertIsNone(trader)


if __name__ == '__main__':
    unittest.main()
