import unittest
from datetime import datetime

import pandas as pd

from birdeye_api.ohlcv_endpoint import ohlcv_to_dataframe
from constants import PRICE_COLUMN, TOTAL_VOLUME_COLUMN, TRADING_MINUTE_COLUMN, TOKEN_COlUMN


class TestRunner(unittest.TestCase):
    def test_to_dataframe(self):
        # Given test data
        test_data = {
            "success": True,
            "data": {
                "items": [
                    {
                        "o": 128.27328370924414,
                        "h": 128.6281001340782,
                        "l": 127.91200927364626,
                        "c": 127.97284640184616,
                        "v": 58641.16636665621,
                        "unixTime": 1726670700,
                        "address": "So11111111111111111111111111111111111111112",
                        "type": "15m"
                    },
                    {
                        "o": 127.97284640184616,
                        "h": 128.49450996585105,
                        "l": 127.89354285873108,
                        "c": 128.04188346328968,
                        "v": 47861.13031539581,
                        "unixTime": 1726671600,
                        "address": "So11111111111111111111111111111111111111112",
                        "type": "15m"
                    }
                ]
            }
        }

        # Expected result
        expected_data = {
            TOKEN_COlUMN: ["So11111111111111111111111111111111111111112",
                           "So11111111111111111111111111111111111111112"],
            TRADING_MINUTE_COLUMN: [datetime.utcfromtimestamp(1726670700),
                                    datetime.utcfromtimestamp(1726671600)],
            TOTAL_VOLUME_COLUMN: [58641.16636665621, 47861.13031539581],
            PRICE_COLUMN: [127.97284640184616, 128.04188346328968]
        }
        expected_df = pd.DataFrame(expected_data)

        # When
        result_df = ohlcv_to_dataframe(test_data)

        # Then
        pd.testing.assert_frame_equal(result_df, expected_df)


if __name__ == "__main__":
    unittest.main()
