"""
Implement a non-trivial program employee_analysis.py in Python to complete:

1. Read work logs from CSV files. Ensure that any data are inconsistencies.

2. Process data from 4 November 2024 until 10 of February 2025 and analyse employees’ productivity.

3. Produce weekly and monthly productivity reports based on provided CSV files.

4. Export the results to employee_report.csv file.

5. Extensive test code used to develop the program.76
"""

import pandas as pd # Reference: https://pandas.pydata.org/docs/
from abc import ABC, abstractmethod # Reference: https://docs.python.org/3/library/abc.html#abc.ABC
from word2number import w2n # Reference: https://pypi.org/project/word2number/
import csv
import unittest
from typing import Literal # Reference: https://docs.python.org/3/library/typing.html#typing.Literal
import matplotlib.pyplot as plt # Reference: https://matplotlib.org/stable/api/pyplot_summary.html
import re # Reference: https://docs.python.org/3/library/re.html#re.match
import numpy as np # Reference: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray
 
class DataSet(ABC):
    """
    The abstract class that define the function that will be used in the child class
    which is dataset type including worklogs and performance review.
    Inherits from abc.ABC to prevent direct instantiation.
    """

    def __init__(self, source, start_date=None, end_date=None):
        """Initialize dataset with source and optional date range."""
        # Reference: https://docs.python.org/3/library/typing.html#typing.Union
        # Use | for type hinting in Python 3.10+
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
        self._data: pd.DataFrame | None = None 

        # Double underscore methods like __parse_date are subject to name mangling and are private methods.
        # This means that they are not accessible from outside the class using the name __parse_date.
        # Reference: https://docs.python.org/3/tutorial/classes.html#private-variables
        self._start_date = self.__parse_date(start_date)
        self._end_date = self.__parse_date(end_date)
        self.__load_data(source)


    def get_dataset(self):
        """Return the processed dataset."""
        return self._data
    

    def set_dates(self, start_date, end_date):
        """Set the date range for filtering."""
        self._start_date = self.__parse_date(start_date)
        self._end_date = self.__parse_date(end_date)

    
    @staticmethod
    def __parse_date(date_str):
        """Validate and Parse date string into datetime object."""
        if not date_str:
            return None
        try:
            # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html
            return pd.to_datetime(date_str, dayfirst=True)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
        

    def __load_data(self, source):
        """Load data from source, either the file path or copy from DataFrame"""
        if isinstance(source, str):
            self._data = self.__read_csv(source)
        elif isinstance(source, pd.DataFrame):
            self._data = source.copy()
        else:
            raise TypeError("Source must be a file path or DataFrame")

    @staticmethod
    def __read_csv(file):
        """
        Helper function that uses CSV reader to read a CSV file and returns a pandas DataFrame.
        """
        with open(file, 'r') as csvfile:
            # Use the csv module to read the file
            reader = csv.reader(csvfile)
            # Read the records into a list
            records = list(reader)
            # Create a DataFrame from the records
            # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.copy.html
            data = pd.DataFrame(records[1:], columns=records[0])
        return data
    

    def __add__(self, other):
        """
        Merge two datasets on Employee Number.
    
        Magic method: override the `+` operator for DataSet objects.
        Reference: https://docs.python.org/3/reference/datamodel.html#object.__add__
        """
        if isinstance(other, DataSet):
            # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge.html
            return pd.merge(
                self.get_dataset(),
                other.get_dataset(),
                on='Employee Number',
                how='outer'
            )
        raise TypeError("Can only merge with another DataSet")


    @abstractmethod
    def clean_data(self):
        """
        All the cleaning and preprocessing are carried out by subclasses.
        Abstract method: subclasses must implement this method.
        Reference: https://docs.python.org/3/library/abc.html#abc.abstractmethod
        """
        pass


class Worklogs(DataSet):
    """
    Class for worklogs dataset.
    Inherits from DataSet.
    """

    def __init__(self, file, start_date=None, end_date=None):
        """The constructor of Worklogs class"""
        super().__init__(file, start_date, end_date)

    def clean_data(self):
        """
        Clean and preprocess the data.

        Part 1: Modify 'Hours Worked', replacing words with numbers.
        Part 2: Convert 'Date' column to datetime format and remove invalid rows.
        part 3: Filter the data by date range
        Part 4: Check the employee name and employee number
        """

        # 1. Modify 'Hours Worked', replacing words with numbers.
        self.__replace_words_number()

        # 2. Identify and replace invalid value in Date Column
        self._data["Date"] = pd.to_datetime(self._data["Date"], format="mixed", errors="coerce")

        # 3. Filter the data out of range
        self.__filter_date(self._start_date, self._end_date)

        # 4. Correct the invalid name or null name
        self.__correct_name()

    def __replace_words_number(self):
        """
        Note: This is meant to be a private function that should not be called outside the object
        Helper function that converts words to numbers
        """

        def word_to_number(text):
            # try parse the word to number and convert to lowercase to handle case-insensitivity
            try:
                return w2n.word_to_num(str(text).lower())
            except:
                # Return the original value if not a recognized number word
                return text

        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_numeric.html
        not_numeric = pd.to_numeric(self._data['Hours Worked'], errors='coerce').isnull()
        self._data.loc[not_numeric, 'Hours Worked'] = self._data.loc[not_numeric, 'Hours Worked'].apply(
            word_to_number)
        self._data['Hours Worked'] = pd.to_numeric(self._data['Hours Worked'], errors='coerce').round(2)

    def __correct_name(self):
        """
        Correct the invalid or null names using a reference derived from valid employee data.
        """

        def correct_name_row(row, reference):
            employee_number = row["Employee Number"]
            if employee_number in reference.index:
                row["First Name"] = reference.loc[employee_number, "First Name"]
                row["Last Name"] = reference.loc[employee_number, "Last Name"]
            return row

        # Create a reference DataFrame from valid names
        name_df = pd.DataFrame(self._data, columns=["Employee Number", "First Name", "Last Name"])

        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop_duplicates.html
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.set_index.html
        reference = (
            name_df[name_df["Last Name"] != ""]
            .drop_duplicates(subset="Employee Number", keep="first")
            .set_index("Employee Number")[["First Name", "Last Name"]]
        )

        # Apply corrections and assign back to self._data
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
        self._data = self._data.apply(lambda row: correct_name_row(row, reference), axis=1)

    def __filter_date(self, start_date=None, end_date=None):
        """
        Note: This is meant to be a private function that should not be called outside the object
        Filter the data by date range
        """
        if start_date is None or end_date is None:
            return

        # Filter the data based on the date range, if the date is out of the range, delete this row
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.between.html
        self._data = self._data[self._data['Date'].between(start_date, end_date)]


class PerformanceReview(DataSet):
    """
    Class for performance review dataset.
    Inherits from DataSet.
    """
    def __init__(self, file):
        super().__init__(file)

    def clean_data(self):
        pass


class EmployeeAnalyser:
    """Main class for employee analysis."""

    def __init__(self, worklogs_file, performance_file, start_date=None, end_date=None):
        """init method"""
        self._start_date = self.__parse_date(start_date)
        self._end_date = self.__parse_date(end_date)
        self.worklogs = Worklogs(worklogs_file)
        self.reviews = PerformanceReview(performance_file)

        # Clean data
        self.worklogs.clean_data()
        self.reviews.clean_data()

        # Merge datasets
        self.data = self.worklogs + self.reviews
        self.additional_columns()

        # backup for original data
        self.original_data = self.data.copy()

        # filter the data with start and end dates
        self.set_dates(start_date, end_date)


    def set_dates(self, start=None, end=None):
        self._start_date = self.__parse_date(start)
        self._end_date = self.__parse_date(end)
        self.filter_date()


    @staticmethod
    def __parse_date(date_str):
        """
        Validate and Parse date string into datetime object.
        Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html
        """
        if not date_str:
            return None
        try:

            return pd.to_datetime(date_str, dayfirst=True)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
        

    def filter_date(self):
        """
        Filter the data by date range
        """
        # Filter the data based on the date range, if the date is out of the range, delete this row
        if self._start_date and self._end_date:
            self.data = self.original_data[self.original_data['Date_x'].between(self._start_date, self._end_date)]
        else:
            self.data = self.original_data


    def export_original_data(self):
        self.original_data.to_csv("original_data.csv")


    def additional_columns(self):
        """
        Datetime columns use for grouping and sorting
        """
        # Create a full employee label: "First Last (Employee Number)"
        self.data['Employee'] = self.data['First Name'] + ' ' + self.data['Last Name'] + ' (' + self.data[
            'Employee Number'].astype(str) + ')'

        # Create a full list of Datetime columns use for grouping and sorting
        self.data['Date_x'] = pd.to_datetime(self.data['Date_x'], format='%d/%m/%Y')
        self.data['Week'] = self.data['Date_x'].dt.isocalendar().week
        self.data['Year'] = self.data['Date_x'].dt.isocalendar().year
        self.data['Month'] = self.data['Date_x'].dt.month
        self.data['Weekday'] = self.data['Date_x'].dt.weekday
        self.data['Year_weekly'] = self.data['Year'].astype(str) + '-W' + self.data[
            'Week'].astype(str).str.zfill(2)
        self.data['Year_monthly'] = self.data['Date_x'].dt.strftime('%Y-%m')
        self.data['Quarter'] = self.data['Date_x'].dt.to_period('Q')


    def summary(self, frequency: Literal['weekly', 'monthly', 'Weekday', 'total'] = 'weekly'):
        """
        Generate a summary based on the specified frequency.

        Parameters:
        - frequency (Literal['weekly', 'monthly', 'weekday']): The time frequency for grouping data.
            Options are 'weekly', 'monthly','weekday'. Default is 'weekly'.

        Returns:
        - Summary data grouped by the specified frequency.
        """

        group_data = self.data.copy()
        if frequency == 'weekly':
            index_col = ['Year_weekly','Employee']
        elif frequency == 'monthly':
            index_col = ['Year_monthly','Employee']
        elif frequency == 'Weekday':
            index_col = ['Weekday','Employee']
        elif frequency == 'total':
            index_col = ['Employee']

        grouped = group_data.groupby(index_col)['Hours Worked'].agg(
            ['mean', 'median', 'min', 'max', 'count'])
        grouped.columns = ['Avg Hours Worked', 'Median Hours Worked',
                           'Min Hours Worked', 'Max Hours Worked','Number of Days Worked']
        grouped = grouped.round(2).reset_index()
        grouped.to_csv(f'summary_{frequency}.csv', index=False)

        return grouped


    @staticmethod
    def __get_overtime(hours):
        """
        Helper function that converts words to numbers and filters numbers
        Input: String
        Output: Integer
        """
        hours = float(hours)
        if hours > 7.5:
            return hours - 7.5
        else:
            return 0

    def overtime(self,frequency: Literal['weekly','total'] = 'total'):
        """
        Helper function that the calculates total overtime hours worked by employees
        Input: String
        Output: Integer
        """
        if frequency == 'weekly':
            index_col = ['Year_weekly', 'Employee']
        else:
            index_col = ['Employee']
        # Create a new column for overtime hours
        dataset = self.data.copy()
        dataset['Overtime'] = dataset['Hours Worked'] - 7.5
        dataset['Overtime'] = dataset['Overtime'].apply(lambda x: x if x > 0 else 0)

        # Group by employee and sum overtime hours
        grouped = dataset.groupby(index_col)['Overtime'].sum()
        grouped.columns = ['Overtime']
        grouped = grouped.round(2).reset_index()

        # Export to CSV
        grouped.to_csv(f'overtime_{frequency}.csv',index=False)

        return grouped   
    

    def productivity_analysis(self):
        data_to_productivity = self.data.copy()

        # Extract performance score from reviews
        data_to_productivity['Performance Score'] = data_to_productivity['Performance Review'].str.extract(r'(\d)').astype(int)

        # Group by employee and performance score, calculate median hours and entry count
        data_to_productivity = data_to_productivity.groupby(['Employee', 'Performance Score'])['Hours Worked'].agg(
            ['median', 'count']).reset_index()

        # Calculate the maximum days worked across all employees
        max_days = data_to_productivity['count'].max()

        # Calculate days missed penalty
        data_to_productivity['days_missed_penalty'] = (max_days - data_to_productivity['count']) / max_days

        # Calculate Adjusted Efficiency
        data_to_productivity['productivity_score'] = data_to_productivity['Performance Score'] / \
            (data_to_productivity['median'] * (1 + data_to_productivity['days_missed_penalty']))*100

        # Assign rank based on Adjusted Efficiency (higher is better)
        data_to_productivity['productivity_rank'] = data_to_productivity['productivity_score'].rank(ascending=False, method='dense').astype(int)

        data_to_productivity = data_to_productivity[['Employee','productivity_score','productivity_rank']].round(2)
        # Save results
        data_to_productivity.to_csv('productivity_analysis.csv', index=False)

        return data_to_productivity

    def quarterly_performance(self):
        data_add1 = self.data.copy()

        employee_quarterly = data_add1.groupby(['Quarter', 'Employee'])['Hours Worked'].agg(
            ['median']).reset_index()
        overall_quarterly = data_add1.groupby(['Quarter'])['Hours Worked'].agg(['median']).reset_index().rename(
            columns={'median': 'overall_median'})
        quarterly_performance = pd.merge(employee_quarterly, overall_quarterly, how='left', on='Quarter')
        quarterly_performance['diff'] = quarterly_performance['median'] - quarterly_performance['overall_median']
        quarterly_pivot = quarterly_performance.pivot(index=['Employee'], columns='Quarter',
                                                      values='diff').reset_index().round(2)
        quarterly_pivot.to_csv('quarterly_performance.csv', index=False)

        return quarterly_pivot
    

    def weekend_compensation(self):
        data_add2 = self.data.copy()
        # create new column
        data_add2["IsWeekend"] = data_add2["Weekday"] >= 5

        # Find out the daily deficit for weekday
        data_add2["Weekday_Deficit"] = data_add2.apply(
            lambda row: max(0, 7.5 - row["Hours Worked"]) if not row["IsWeekend"] else 0,
            axis=1
        )

        # separate the weekday hours from weekend
        data_add2["Weekend_Hours"] = data_add2.apply(
            lambda row: row["Hours Worked"] if row["IsWeekend"] else 0,
            axis=1
        )

        # Group by weekly
        weekly = data_add2.groupby(["Employee", "Year_weekly"]).agg(Total_Weekday_Deficit=("Weekday_Deficit", "sum"),
                                                        Total_Weekend_Hours=("Weekend_Hours", "sum"))

        # If the weekend compensate the weekday deficit
        weekly["Weekend_Compensates"] = weekly["Total_Weekend_Hours"] >= weekly["Total_Weekday_Deficit"]

        # Then we find out the percentage of compensation for the period
        agg = (
            weekly.groupby("Employee")
            .agg({
                "Total_Weekday_Deficit": "mean",
                "Total_Weekend_Hours": "mean",
                "Weekend_Compensates": "mean",  # percentage of weeks fully compensated
            })
            .rename(columns={"Weekend_Compensates": "Compensated_Weeks_Ratio"})
        )

        # We would also like to compare with the Performance Score to see if there is relationship
        employee_score = data_add2[["Employee", "Performance Review"]].drop_duplicates(subset="Employee")
        agg = pd.merge(agg, employee_score, on="Employee", how="left")

        agg = agg.round(2)
        # Reset index for a table
        result = agg.reset_index().drop(columns=["index"])

        result.to_csv('weekday weekend comparison.csv', index=False)

        return result


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


    def is_valid_date(self, date_values, date_type='normal'):
        """
        Check if the date string is in the correct format.
        """
        if date_type == 'normal':
            # Check if the date is mixed datetime format, e.g. '2024-11-04' or '04/11/2024'
            self.assertTrue(
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
            self.assertIn(
                employee_number, reference_mapping,
                f"Invalid employee number: {employee_number} not found in reference."
            )
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
        self.do_test_summary('Weekday')
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
            
        
if __name__ == '__main__':
    # Define the file path and timeframe here
    file_worklogs = "employee_worklogs.csv"
    file_performance_review = "employee_performance_review.csv"
    start_date = "04/11/2024"
    end_date = "10/02/2025"

    # Run the program here
    analyser = EmployeeAnalyser(file_worklogs, file_performance_review, start_date=start_date, end_date=end_date)


    # # Question 1 and 7
    # analyser.summary(frequency='weekly')
    # analyser.summary(frequency='weekday')
    # analyser.summary(frequency='total')
    #
    # # Question 2 and 8
    # analyser.summary(frequency='monthly')
    #
    # # Question 3 and 4
    # analyser.overtime(frequency='weekly')
    # analyser.overtime(frequency='total')

    # Question 5 and 6
    # analyser.productivity_analysis()

    # # additional features
    # analyser.quarterly_performance()
    # analyser.weekend_compensation()
    # analyser.set_dates()  # if no parameter then reset to original (no filtering) -> no output, just filtering
    # analyser.export_original_data()
 
    # test the analyser
    unittest.main(exit=False)

