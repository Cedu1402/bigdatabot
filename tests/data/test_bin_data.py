import unittest

import pandas as pd

from data.feature_engineering import bin_data


# Import your bin_data function here
# from your_module import bin_data

class TestRunner(unittest.TestCase):

    def setUp(self):
        # Define example data
        self.data = [
            pd.DataFrame({"A": [1, 5, 10, 15]}),
            pd.DataFrame({"A": [2, 8, 12, 18]})
        ]
        self.columns = ["A"]
        self.bin_edges = {"A": [0, 5, 10, 15]}  # 0-5, 5-10, 10-15 bins

    def test_binning_correctness(self):
        # Run the binning function
        result = bin_data(self.data, self.columns, self.bin_edges)

        # Check the binned values
        expected_binned_data = [
            pd.DataFrame({"A": [1, 2, 3, 4]}),  # Binned values for the first DataFrame
            pd.DataFrame({"A": [1, 2, 3, 4]})  # Binned values for the second DataFrame
        ]

        for res_df, expected_df in zip(result, expected_binned_data):
            pd.testing.assert_frame_equal(res_df, expected_df)

    def test_data_length_preserved(self):
        # Ensure data length is unchanged
        result = bin_data(self.data, self.columns, self.bin_edges)
        self.assertEqual(len(result), len(self.data))
        for original_df, result_df in zip(self.data, result):
            self.assertEqual(len(original_df), len(result_df))

    def test_data_structure_preserved(self):
        # Ensure the column structure is the same
        result = bin_data(self.data, self.columns, self.bin_edges)
        for original_df, result_df in zip(self.data, result):
            self.assertListEqual(list(original_df.columns), list(result_df.columns))

    def test_no_additional_columns(self):
        # Check that no extra columns were added
        result = bin_data(self.data, self.columns, self.bin_edges)
        for df in result:
            self.assertNotIn('_df_index', df.columns)


if __name__ == '__main__':
    unittest.main()
