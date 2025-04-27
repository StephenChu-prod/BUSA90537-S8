import pandas as pd
from abc import ABC, abstractmethod
from word2number import w2n
import csv
import unittest
from typing import Literal
from Dataset import *
from EmployeeAnalyser import *


class TestAnalyser(unittest.TestCase):
    """
    Test class for EmployeeAnalyser
    """

    def setUp(self):
        """
        Set up the test environment.
        Create a EmployeeAnalyser instance with test data.
        """

        file_worklogs = "employee_worklogs.csv"
        file_performance_review = "employee_performance_review.csv"
        start_date = "04/11/2024"
        end_date = "10/02/2025"

        self.analyser = EmployeeAnalyser(file_worklogs, file_performance_review, start_date=start_date,
                                         end_date=end_date)

    def do_test(self, input, expected):
        """
        Test the EmployeeAnalyser class with given parameters and expected output.
        """
        self.assertEqual(expected, input)

    def test_summary(self):
        """
        Test the summary method of EmployeeAnalyser class.
        """
        pass
