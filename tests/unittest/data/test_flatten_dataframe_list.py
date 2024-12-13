import unittest

import pandas as pd

from data.data_split import flatten_dataframe_list


class TestRunner(unittest.TestCase):

    def setUp(self):
        """Set up some example DataFrames for testing"""
        # Create sample DataFrames for testing
        self.df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        self.df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        self.df3 = pd.DataFrame({'A': [9, 10], 'B': [11, 12]})

        # List of DataFrames
        self.data = [self.df1, self.df2, self.df3]

    def test_flatten_dataframe_list(self):
        """Test that the function correctly flattens the list of DataFrames"""
        result = flatten_dataframe_list(self.data)

        # Expected flattened DataFrame
        expected_result = pd.DataFrame({'A': [2, 6, 10], 'B': [4, 8, 12]})

        # Assert that the resulting DataFrame matches the expected result
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)

    def test_empty_list(self):
        """Test that an empty list returns an empty DataFrame"""
        result = flatten_dataframe_list([])
        expected_result = pd.DataFrame()
        pd.testing.assert_frame_equal(result, expected_result)

    def test_single_dataframe(self):
        """Test that if only one DataFrame is passed, it returns its last row"""
        result = flatten_dataframe_list([self.df1])
        expected_result = pd.DataFrame({'A': [2], 'B': [4]})
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)

    def test_one_column(self):
        """Test that it works with DataFrames with only one column"""
        df_single_col = pd.DataFrame({'A': [1, 2, 3]})
        result = flatten_dataframe_list([df_single_col])
        expected_result = pd.DataFrame({'A': [3]})
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)
