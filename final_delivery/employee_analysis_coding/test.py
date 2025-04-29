import pandas as pd # Reference: https://pandas.pydata.org/docs/
from word2number import w2n # Reference: https://pypi.org/project/word2number/
import csv
import unittest
from typing import Literal # Reference: https://docs.python.org/3/library/typing.html#typing.Literal
import re # Reference: https://docs.python.org/3/library/re.html#re.match
import numpy as np # Reference: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray
from dataset import *
from employee_analysis import *


class TestAnalyser(unittest.TestCase):
    """
    Test class for EmployeeAnalyser
    """
    
    def setUp(self):
        """
        Set up the test environment.
        Create a EmployeeAnalyser instance with test data.
        """

        # Create dummy test data for worklogs
        # Create the test worklogs DataFrame exactly matching the image
        worklogs_data = {
            'Employee Number': [105, 101, 105, 105, 101, 102, 102, 105, 104, 104, 104, 102, 103, 103, 104, 104, 104, 102, 104, 103],
            'First Name': [
                'Emma', 'Alice', 'Emma', 'Emma', 'Alice',
                'Bob', 'Bob', 'Emma', 'David', 'David', 'David',
                'Bob', 'Charlie', 'Charlie', 'David', 'David', 'David',
                'Bob', 'David', 'Charlie'
            ],
            'Last Name': [
                'Davis', 'Johnson', 'Davis', 'Davis', 'Johnson',
                'Smith', 'Smith', 'Davis', 'Wilson', 'Wilson', 'Wilson',
                'Smith', 'Brown', 'Brown', 'Wilson', 'Wilson', 'Wilson',
                'Smith', 'Wilson', 'Brown'
            ],
            'Date': [
                '11/26/2024', '11/12/2024', '12/27/2024', '12/17/2024', '01/30/2025',
                '11/09/2024', '11/20/2024', '12/19/2024', '12/12/2024', '12/28/2024', '12/17/2024',
                '11/22/2024', '12/18/2024', '12/17/2024', '12/09/2024', '12/18/2024', '12/20/2024',
                '01/24/2025', '01/02/2025', '11/04/2024'
            ],
            'Hours Worked': [
                9.35, 7.32, 6.8, 8.72, 5.98,
                3.62, 6.55, 5.2, 5.96, 5.81, 7.07,
                5.04, 7.8, 2.23, 3.19, 7.31, 5.0,
                2.55, 2.05, 9.81
            ]
        }

        worklogs_df = pd.DataFrame(worklogs_data)
        worklogs_df.to_csv('test_employee_worklogs.csv', index=False)

        # Create the test performance review DataFrame
        performance_review_data = {
            'Employee Number': [103, 102, 105, 101, 104],
            'Date': ['2/15/2025', '2/21/2025', '2/16/2025', '2/11/2025', '2/12/2025'],
            'Performance Review': [
                '5 - Exceeding Expectations',
                '4 - Meeting Expectations',
                '3 - Satisfactory',
                '3 - Satisfactory',
                '4 - Meeting Expectations'
            ]
        }
        performance_df = pd.DataFrame(performance_review_data)
        performance_df.to_csv('test_employee_performance_review.csv', index=False)


        file_worklogs = "test_employee_worklogs.csv"
        file_performance_review = "test_employee_performance_review.csv"
        start_date = "04/11/2024"
        end_date = "10/02/2025"

        # # Create a test dataset
        # file_worklogs = "test_employee_worklogs.csv"
        # file_performance_review = "test_employee_performance_review.csv"

        self.analyser = EmployeeAnalyser(file_worklogs, file_performance_review, start_date=start_date,
                                         end_date=end_date)


    def do_test(self, input, expected):
        """
        Test the EmployeeAnalyser class with given parameters and expected output.
        """
        # Reference: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual
        self.assertEqual(expected, input)


    def is_valid_date(self, date_values, date_type='normal'):
        """
        Check if the date string is in the correct format.
        """
        if date_type == 'normal':
            # Check if the date is mixed datetime format, e.g. '2024-11-04' or '04/11/2024'
            self.assertTrue(
                # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.api.types.is_datetime64_any_dtype.html
                pd.api.types.is_datetime64_any_dtype(date_values),
                f"Invalid date format: {date_type} date should be in 'YYYY-MM-DD' or 'DD/MM/YYYY' format."
            )
            # Check if the date is in the range of start_date and end_date
            self.assertTrue(
                date_values.between(self.analyser.worklogs._start_date, self.analyser.worklogs._end_date).all(),
                f"Invalid date range: {date_type} date should be between \
                {self.analyser.worklogs._start_date} and {self.analyser.worklogs._end_date}."
            )

        elif date_type == 'monthly':
            # Check if the date is in 'YYYY-MM' format, and MM is 01-12
            # Regex Matching Reference: https://docs.python.org/3/library/re.html#re.match
            for value in date_values:
                #  Reference: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertRegex
                self.assertRegex(
                    value, r'^\d{4}-(0[1-9]|1[0-2])$',
                    f"Invalid date format: {date_type} date should be in 'YYYY-MM' format."
                )

        elif date_type == 'weekly':
            # Check if the date is in 'YYYY-WW' format, and WW is 01-53
            for value in date_values:
                self.assertRegex(
                    value, r'^\d{4}-W(0[1-9]|[1-4][0-9]|5[0-3])$',
                    f"Invalid date format: {date_type} date should be in 'YYYY-WW' format."
                )
 
        elif date_type == 'Weekday':
            # Check if the date is a number in range of (0,6), where 0 is Monday and 6 is Sunday
            for value in date_values:
                # Reference: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertTrue
                self.assertTrue(
                    isinstance(value, (int, np.integer)) and 0 <= value <= 6,
                    f"Invalid date format: {date_type} date should be in range of (0,6)."
                )


    def is_valid_number(self, summary, colums, frequency):
        """
        Check if selected columns in the summary DataFrame contain valid numbers.
        """
        for col in summary.columns:
            if col not in colums:
                continue  # Skip non-numeric columns

            for val in summary[col]:
                # Reference: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertIsInstance
                self.assertIsInstance(
                    val, (int, float),
                   f"Invalid type: {frequency}'s value should be a number."
                )

    
    def is_valid_name(self, name_series):
        """
        Check if the name is in the correct format.
        """
        # Reference mapping for employee numbers to names
        reference_mapping = {
            '101': 'Alice Johnson',
            '102': 'Bob Smith',
            '103': 'Charlie Brown',
            '104': 'David Wilson',
            '105': 'Emma Davis'
        } 
        for name in name_series:
            # Check if the name is in 'First Last (Employee Number)' format
            match = re.match(r'^([A-Za-z]+(?: [A-Za-z]+)*) \((\d{3})\)$', name)
            self.assertRegex(
                name, r'^([A-Za-z]+(?: [A-Za-z]+)*) \((\d{3})\)$',
                f"Invalid name format: employee should be in 'First Last (Employee Number)' format."
            )

            # Check if the name is empty
            self.assertNotEqual(
                name, '', f"Invalid name: employee name should not be empty."
            )

            # Check if the name matches the employee number
            extracted_name = match.group(1)      # 'Alice Johnson'
            employee_number = match.group(2)      # '101'
            # Check if the employee number is in the reference mapping
            # Reference: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertIn
            self.assertIn(
                employee_number, reference_mapping,
                f"Invalid employee number: {employee_number} not found in reference."
            )
            
            # Check if the extracted name matches the reference mapping
            self.assertEqual(
                extracted_name, reference_mapping[employee_number],
                f"Invalid name: {extracted_name} does not match employee number {employee_number}."
            )


    
    def do_test_summary(self, frequency):
        """
        Test the summary method with given parameters and expected output.
        """
        summary_data = self.analyser.summary(f'{frequency}')

        # Test if total hours worked is a number
        numeric_cols = ['Avg Hours Worked', 'Median Hours Worked', 'Min Hours Worked', 'Max Hours Worked', 'Number of Days Worked']
        self.is_valid_number(summary_data, numeric_cols, f'{frequency}')

        # Test if date is in the correct format
        if frequency == 'monthly' or frequency == 'weekly':
            self.is_valid_date(summary_data[f'Year_{frequency}'], f'{frequency}')
        elif frequency == 'Weekday':
            self.is_valid_date(summary_data['Weekday'], f'{frequency}')

        # Test if employee name is in the correct format
        self.is_valid_name(summary_data['Employee'])


    def test_summary(self):
        """
        Test if summary method result is valid.
        """
        # Test if summary_monthly is valid
        self.do_test_summary('monthly')
        # Test if summary_weekly is valid
        self.do_test_summary('weekly')
        # Test if summary_weekday is valid
        # self.do_test_summary('Weekday')
        # Test if summary_total is valid
        self.do_test_summary('total')


    def test_productivity_analysis(self):
        """
        Test if productivity analysis method result is valid.
        """
        productivity = self.analyser.productivity_analysis()
        # Test if productivity score is a number
        self.assertTrue(
            pd.api.types.is_numeric_dtype(productivity['productivity_score']),
            "productivity_score column should be numeric"
        )
        # Test if productivity rank is a number
        self.assertTrue(
            pd.api.types.is_numeric_dtype(productivity['productivity_rank']),
            "productivity_rank column should be numeric"
        )

        # Test if the productivity rank is in the range of 1 to 5
        self.assertTrue(
            all(1 <= rank <= 5 for rank in productivity['productivity_rank']),
            "productivity_rank should be in the range of 1 to 5"
        )

        # Test if employee name is in the correct format
        self.is_valid_name(productivity['Employee'])


    def test_overtime(self):
        """
        Test if overtime method result is valid.
        """
        overtime_weekly = self.analyser.overtime('total')
        numeric_cols = ['Overtime']
        # Test if total overtime is a number
        self.is_valid_number(overtime_weekly, numeric_cols, 'overtime_weekly') 
        # Test if employee name is in the correct format
        self.is_valid_name(overtime_weekly['Employee'])
        
        total_overtime = self.analyser.overtime('weekly')
        # Test if total overtime is a number
        self.is_valid_number(total_overtime, numeric_cols, 'total_overtime')
        # Test if employee name is in the correct format
        self.is_valid_name(total_overtime['Employee'])
        # Test if the date is in the correct format
        self.is_valid_date(total_overtime['Year_weekly'], 'weekly')

    
    def test_quarterly_performance(self):
        """
        Test if quarterly performance method result is valid.
        """
        quarterly_performance = self.analyser.quarterly_performance()
        # Test if the date is in the correct format
        numeric_cols = ['2024Q4', '2025Q1']
        self.is_valid_number(quarterly_performance, numeric_cols, 'quarterly performance')
        # Test if employee name is in the correct format
        self.is_valid_name(quarterly_performance['Employee'])

    
    def test_weekend_compensation(self):
        """
        Test if weekend compensation method result is valid.
        """
        weekend_compensation = self.analyser.weekend_compensation()
        # Test if the date is in the correct format
        numeric_cols = ['Total_Weekday_Deficit', 'Total_Weekend_Hours', 'Compensated_Weeks_Ratio']
        self.is_valid_number(weekend_compensation, numeric_cols, 'weekend compensation')
        # Test if employee name is in the correct format
        self.is_valid_name(weekend_compensation['Employee'])

        # Reference valid mapping
        valid_reviews = {
            '5 - Exceeding Expectations',
            '4 - Meeting Expectations',
            '3 - Satisfactory'
        }

        # Test if performance review is in the valid mapping
        for review in weekend_compensation['Performance Review']:
            self.assertIn(
                review,
                valid_reviews,
                f"Invalid Performance Review value found: {review}"
            )

unittest.main(exit=False)