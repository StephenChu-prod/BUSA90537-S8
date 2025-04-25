"""
Implement a non-trivial program employee_analysis.py in Python to complete:

1. Read work logs from CSV files. Ensure that any data are inconsistencies.

2. Process data from 4 November 2024 until 10 of February 2025 and analyse employees’ productivity.

3. Produce weekly and monthly productivity reports based on provided CSV files.

4. Export the results to employee_report.csv file.

5. Extensive test code used to develop the program.76
"""

import pandas as pd
from abc import ABC, abstractmethod
from word2number import w2n
import csv
import unittest
from typing import Literal


class DataSet(ABC):
    """
    The abstract class that define the function that will be used in the child class
    """

    def __init__(self, source, start_date=None, end_date=None):
        """Initialize dataset with source and optional date range."""
        self._data = None
        self._start_date = self.__parse_date(start_date)
        self._end_date = self.__parse_date(end_date)
        self.__load_data(source)

    def get_dataset(self):
        """Return the processed dataset."""
        return self._data

    def set_dates(self, start_date, end_date):
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
        """Merge two datasets on Employee Number."""
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
        """All the cleaning and preprocessing are carried out by subclasses."""
        pass


class Worklogs(DataSet):
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

        self.__replace_number_words()
        # 2. Identify and replace invalid value in Date Column
        self._data["Date"] = pd.to_datetime(self._data["Date"], format="mixed", errors="coerce")

        # 3. Filter the data out of range
        self.__filter_date(self._start_date, self._end_date)

        # 4. Correct the invalid name or null name
        self.__correct_name()

    def __replace_number_words(self):
        """
        Note: This is meant to be a private function that should not be called outside the object
        Helper function that converts numbers to words
        """

        def word_to_number(text):
            # try parse the word to number and convert to lowercase to handle case-insensitivity
            try:
                return w2n.word_to_num(str(text).lower())
            except:
                # Return the original value if not a recognized number word
                return text

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
        reference = (
            name_df[name_df["Last Name"] != ""]
            .drop_duplicates(subset="Employee Number", keep="first")
            .set_index("Employee Number")[["First Name", "Last Name"]]
        )

        # Apply corrections and assign back to self._data
        self._data = self._data.apply(lambda row: correct_name_row(row, reference), axis=1)

    def __filter_date(self, start_date=None, end_date=None):
        """
        Note: This is meant to be a private function that should not be called outside the object
        Filter the data by date range
        """
        if start_date is None or end_date is None:
            return

        # Filter the data based on the date range, if the date is out of the range, delete this row
        self._data = self._data[self._data['Date'].between(start_date, end_date)]


class PerformanceReview(DataSet):
    def __init__(self, file):
        super().__init__(file)

    def clean_data(self):
        pass


class EmployeeAnalyser:
    """Main class for employee analysis."""

    def __init__(self, worklogs_file, performance_file, start_date=None, end_date=None):
        """init method"""
        self.worklogs = Worklogs(worklogs_file, start_date, end_date)
        self.reviews = PerformanceReview(performance_file)

        # Clean data
        self.worklogs.clean_data()
        self.reviews.clean_data()

        # Merge datasets
        self.data = self.worklogs + self.reviews
        self.additional_columns()
        self.out_data = self.data.copy()

    def output(self):
        """
        Output the data to a CSV file
        """
        if not self.out_data:
            print('there is no output')
        self.out_data.to_csv('analyser.csv', index=False)

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
        self.data['Year_week'] = self.data['Year'].astype(str) + '-W' + self.data[
            'Week'].astype(str).str.zfill(2)
        self.data['Year_month'] = self.data['Date_x'].dt.strftime('%Y-%m')

    def summary(self, frequency: Literal['weekly', 'monthly', 'weekday', 'total'] = 'weekly', pivot: bool = False):
        """
        Generate a summary based on the specified frequency and pivot option.

        Parameters:
        - frequency (Literal['weekly', 'monthly', 'weekday']): The time frequency for grouping data.
            Options are 'weekly', 'monthly','weekday'. Default is 'weekly'.
        - pivot (bool): Whether to pivot the resulting DataFrame. Default is False.

        Returns:
        - Summary data grouped by the specified frequency.
        """
        if frequency == 'weekly':
            grouped = self.data.groupby(['Year_week', 'Employee'])['Hours Worked'].agg(['sum']).reset_index()
            # print(grouped.head())
            grouped.columns = ['Year_week', 'Employee', 'Hours Worked']
            index_col = 'Year_week'
        elif frequency == 'monthly':
            grouped = self.data.groupby(['Year_month', 'Employee'])['Hours Worked'].sum().reset_index()
            index_col = 'Year_month'
        elif frequency == 'weekday':
            grouped = self.data.groupby(['Weekday', 'Employee'])['Hours Worked'].sum().reset_index()
            index_col = 'Weekday'
        elif frequency == 'total':
            grouped = self.data.groupby(['Employee'])['Hours Worked'].sum().reset_index()
            index_col = 'Employee'
        else:
            raise ValueError("Invalid frequency. Choose 'weekly' or 'monthly'.")

        # output
        grouped['Hours Worked'] = grouped['Hours Worked'].round(2)
        if pivot:
            pivoted = grouped.pivot(index=index_col, columns='Employee', values='Hours Worked')
            pivoted.to_csv(f'pivoted_summary_{frequency}.csv')
        else:
            grouped.to_csv(f'grouped_summary_{frequency}.csv', index=False)

    # @staticmethod
    # def __get_overtime(hours):
    #     """
    #     Helper function that converts words to numbers and filters numbers
    #     Input: String
    #     Output: Integer
    #     """
    #     hours = float(hours)
    #     if hours > 7.5:
    #         return hours - 7.5
    #     else:
    #         return 0

    # def overtime(self):

    #     # take a copy of the merged data
    #     df = self.data.copy()

    #     # create a new column for the overtime per day
    #     df['Daily Overtime Each Employee'] = df['Hours Worked'].apply(self.__get_overtime)

    #     # group the data and sum them up
    #     df['Total_Overtime'] = \
    #         df.groupby('Employee Number')[['Daily Overtime Each Employee']].transform('sum','median').round(2)
    #     df['Weekly_overtime'] = df.groupby(['Year_week', 'Employee'])[
    #         'Daily Overtime Each Employee'].transform('mean').round(2)

    #     # drop any duplicated rows, and unused columns
    #     overtime_summary = df[['Year_week', 'Employee', 'Weekly_overtime',
    #                            'Total_Overtime']]
    #     overtime_summary = overtime_summary.groupby(['Year_week', 'Employee'])[
    #         ['Weekly_overtime', 'Total_Overtime']
    #     ].first().reset_index()

    #     # return the output
    #     overtime_summary.to_csv('overtime_summary.csv', index=False)

    def total_overtime(self):
        """
        Helper function that the calculates total overtime hours worked by employees
        Input: String
        Output: Integer
        """
        # Create a new column for overtime hours
        dataset = self.data.copy()
        dataset['Overtime'] = dataset['Hours Worked'] - 7.5
        dataset['Overtime'] = dataset['Overtime'].apply(lambda x: x if x > 0 else 0)

        # Group by employee and sum overtime hours
        grouped = dataset.groupby(['Employee'])['Overtime'].sum().reset_index()
        grouped.columns = ['Employee', 'Overtime']
        grouped['Overtime'] = grouped['Overtime'].round(2)

        # Show the plot
        
        # Export to CSV
        grouped.to_csv('total_overtime.csv')


    def total_overtime_weekly(self):
        """
        Helper function that the calculates total overtime hours worked by employees
        Input: String
        Output: Integer
        """
        # Create a new column for overtime hours
        dataset = self.data.copy()
        dataset['Overtime'] = dataset['Hours Worked'] - 7.5
        dataset['Overtime'] = dataset['Overtime'].apply(lambda x: x if x > 0 else 0)

        # Group by employee and sum overtime hours
        grouped = dataset.groupby(['Year_week', 'Employee'])['Overtime'].sum().reset_index()
        grouped.columns = ['Year_week', 'Employee', 'Overtime']
        grouped['Overtime'] = grouped['Overtime'].round(2)

        # Show the plot

        # Export to CSV
        grouped.to_csv('total_overtime_weekly.csv')

    def productivity_analysis(self):
        df = self.data.copy()

        # Extract performance score from reviews
        df['Performance Score'] = df['Performance Review'].str.extract(r'(\d)').astype(int)

        # Group by employee and performance score, calculate median hours and entry count
        df = df.groupby(['Employee', 'Performance Score'])['Hours Worked'].agg(
            ['median', 'count']).reset_index()

        # Sort by performance (desc), median hours (asc), count (desc) and reset index
        df = df.sort_values(
            by=['Performance Score', 'median', 'count'],
            ascending=[False, True, False]
        ).reset_index(drop=True)

        # Assign rank based on sorted order
        df['productivity_rank'] = df.index + 1

        # Save results
        df.to_csv('productivity_analysis.csv', index=False)

    def add_2(self):
        df = self.data.copy()
        df["IsWeekend"] = df["Weekday"] >= 5
        # Aggregate by employee & (year, week)
        agg = (
            df.groupby(["Employee","Year_week"])
            .agg(
                Weekday_Hours=("Hours Worked", lambda s: s[~df.loc[s.index, "IsWeekend"]].sum()),
                Weekend_Hours=("Hours Worked", lambda s: s[df.loc[s.index, "IsWeekend"]].sum()),
            ))

        # Required weekday hours are 7.5h × 5days = 37.5h for every full work‑week
        agg["Required_Weekday_Hours"] = 37.5

        # Shortfall during the week (Difference between required weekday hours and actual weekday hours)
        agg["Weekday_Deficit"] = agg["Required_Weekday_Hours"] - agg["Weekday_Hours"]

        # Positive value means weekend work fully covers the deficit (or more)
        agg["Weekend_minus_Deficit"] = agg["Weekend_Hours"] - agg["Weekday_Deficit"]

        # Create a column to show whether the employee use weekend to compensates work hours
        agg["Weekend_Compensates"] = agg[
                                         "Weekend_minus_Deficit"] >= 0  # If True means weekend work fully covers the deficit

        # agg = agg[["Weekday_Deficit","Weekend_Hours","Weekend_minus_Deficit"]]
        agg = agg.round(2)
        # Reset index for a table
        result = agg.reset_index()

        result.to_csv('weekday weekend comparison.csv', index=False)



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
        



if __name__ == '__main__':
    # Define the file path and timeframe here
    file_worklogs = "employee_worklogs.csv"
    file_performance_review = "employee_performance_review.csv"
    start_date = "04/11/2024"
    end_date = "10/02/2025"

    # Run the program here
    analyser = EmployeeAnalyser(file_worklogs, file_performance_review, start_date=start_date, end_date=end_date)

    # Question 1 and 7
    analyser.summary(frequency='weekly')

    # Question 2 and 8
    # analyser.summary(frequency='monthly', pivot=True)

    # Question 3 and 4
    # analyser.overtime()

    # Question 5 and 6
    # analyser.productivity_analysis()

    # additional features
    # analyser.add_2()