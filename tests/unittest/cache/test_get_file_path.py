import os
import unittest

from cache_helper import get_cache_file_path


def are_same_directory(path1, path2):
    """Check if two paths refer to the same directory."""
    abs_path1 = os.path.abspath(os.path.normpath(path1))
    abs_path2 = os.path.abspath(os.path.normpath(path2))
    return abs_path1 == abs_path2


class TestRunner(unittest.TestCase):

    def test_get_cache_file_path(self):
        # Arrange
        file_name = "test"
        expected = os.path.join("../../../cache/", file_name + ".pkl")
        # Act
        actual = get_cache_file_path(file_name)
        # Assert
        self.assertTrue(are_same_directory(expected, actual))