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
import matplotlib.pyplot as plt


class DataSet(ABC):
    """
    The abstract class that define the function that will be used in the child class.
    DataSet is the base class for all datasets which will be read to analyze.
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
            data = pd.DataFrame(records[1:], columns=records[0])
        return data

    def __add__(self, other):
        """Merge two datasets on Employee Number."""
        if isinstance(other, DataSet):
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
    """
    The class that handles the worklogs dataset.
    It inherits from the DataSet class and implements the clean_data method.
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
        # 1. Identify and replace invalid numbers in Hours Worked
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
    """
    The class that handles the performance review dataset.
    """
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
        self.total_hours('all')


    def output(self):
        """
        Output the data to CSV
        """
        self.data.to_csv('analyser.csv', index=False)


    def total_hours(self, frequency: Literal['weekly', 'monthly', 'all']):
        """
        Helper function that calculates total hours worked by employees
        Input: String
        Output: DataFrame
        """
        # Group by employee and frequency, sum hours worked
        if frequency == 'weekly':
            grouped = self.data.groupby(['Year_week', 'Employee'])['Hours Worked'].sum().reset_index()
            grouped.columns = ['Year_week', 'Employee', 'Hours Worked']
            index_col = 'Year_week'
        elif frequency == 'monthly':
            grouped = self.data.groupby(['Year_month', 'Employee'])['Hours Worked'].sum().reset_index()
            grouped.columns = ['Year_month', 'Employee', 'Hours Worked']
            index_col = 'Year_month'
        elif frequency == 'all':
            grouped = self.data.groupby(['Employee'])['Hours Worked'].sum().reset_index()
            grouped.columns = ['Employee', 'Hours Worked']
            index_col = 'Employee'
        else:
            raise ValueError("Invalid frequency. Choose 'weekly' or 'monthly'.")

        # Round hours to 2 decimal place
        grouped['Hours Worked'] = grouped['Hours Worked'].round(2)

        # Pivot the data for plotting
        if frequency == 'all':
            # Export to CSV
            grouped.to_csv('total_hours_all.csv')
        else:
            pivoted_data = grouped.pivot(index=index_col, columns='Employee', values='Hours Worked')
            # Show the plot
            plt.figure(figsize=(12, 6))
            for col in pivoted_data.columns:
                plt.plot(pivoted_data.index, pivoted_data[col], marker='o', label=col)

            plt.title(f'Employee {frequency.capitalize()} Hours Worked')
            plt.xlabel(index_col.replace('_', ' ').capitalize())
            plt.ylabel('Hours Worked')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend(title='Employee', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()
  
            # Export to CSV
            pivoted_data.to_csv(f'total_hours_{frequency}.csv')


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

    
    def productive_employee(self):
        """
        Most productive employee is determined by 3 metrics (from most priority to least):
        (1) Performance Review result (5: most productive, 1: least productive)
        (2) Median of work hours (lower median : higher productivity)
        (3) Count of workday (higher count of workday : higher productivity)
        """
        # Group by employee and performance review, calculate median and count
        grouped = self.data.groupby(['Employee Number', 'Performance Review'])['Hours Worked'].agg(['median', 'count']).reset_index()
        grouped.sort_values(by=['Performance Review', 'median', 'count'], ascending=[False, True, False]).reset_index(drop=True)
        grouped['productivity_rank'] = grouped.index + 1

        # Export to CSV
        grouped.to_csv('productive_employee.csv', index=False)


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

        # Export the data to CSV
        self.data.to_csv('output_CleanData.csv', index=False)

    def summary(self, frequency: Literal['weekly', 'monthly', 'weekday'], pivot: bool = False):
        if frequency == 'weekly':
            grouped = self.data.groupby(['Year_week', 'Employee'])['Hours Worked'].sum().reset_index()
            # print(grouped.head())
            grouped.columns = ['Year_week', 'Employee', 'Hours Worked']
            index_col = 'Year_week'
        elif frequency == 'monthly':
            grouped = self.data.groupby(['Year_month', 'Employee'])['Hours Worked'].sum().reset_index()
            index_col = 'Year_month'
        elif frequency == 'weekday':
            grouped = self.data.groupby(['Weekday', 'Employee'])['Hours Worked'].sum().reset_index()
            index_col = 'Weekday'
        else:
            raise ValueError("Invalid frequency. Choose 'weekly' or 'monthly'.")

        # output
        grouped['Hours Worked'] = grouped['Hours Worked'].round(2)
        if pivot:
            pivoted = grouped.pivot(index=index_col, columns='Employee', values='Hours Worked')
            pivoted.to_csv(f'pivoted_summary_{frequency}.csv')
        else:
            grouped.to_csv(f'grouped_summary_{frequency}.csv', index=False)



if __name__ == '__main__':
    # Define the file path and timeframe here
    file_worklogs = "employee_worklogs.csv"
    file_performance_review = "employee_performance_review.csv"
    start_date = "04/11/2024"
    end_date = "10/02/2025"

    # Run the program here
    analyser = EmployeeAnalyser(file_worklogs, file_performance_review, start_date=start_date, end_date=end_date)