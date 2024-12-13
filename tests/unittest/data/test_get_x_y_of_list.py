import unittest

import pandas as pd

from data.data_split import get_x_y_of_list


# Unit Test Class
class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample DataFrames for the tests
        self.train_data = [pd.DataFrame({'feature1': [1, 2], 'feature2': [3, 4], 'label': [1, 1]}),
                           pd.DataFrame({'feature1': [1, 3], 'feature2': [3, 5], 'label': [0, 0]})]

    def test_get_x_y_of_list(self):
        # Testing the extraction of X and y from the data
        x_data, y_data = get_x_y_of_list(self.train_data)

        # Expected X (features) and y (label) DataFrames
        expected_x = [pd.DataFrame({'feature1': [1, 2], 'feature2': [3, 4]}),
                      pd.DataFrame({'feature1': [1, 3], 'feature2': [3, 5]})]

        expected_y = [1, 0]

        # Assert if the X and y are correctly extracted
        self.assertEqual(len(x_data), len(y_data))
        self.assertEqual(len(x_data), len(expected_x))
        self.assertEqual(len(y_data), len(expected_y))

        self.assertEqual(y_data, expected_y)

        for index, item in enumerate(x_data):
            pd.testing.assert_frame_equal(item, expected_x[index])


if __name__ == '__main__':
    unittest.main()
