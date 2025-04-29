import pandas as pd # Reference: https://pandas.pydata.org/docs/
from abc import ABC, abstractmethod # Reference: https://docs.python.org/3/library/abc.html#abc.ABC
from word2number import w2n # Reference: https://pypi.org/project/word2number/
import csv
from typing import Literal # Reference: https://docs.python.org/3/library/typing.html#typing.Literal
from dataset import *


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
        """
        Set the start and end dates for filtering the data.
        Parameters:
        - start (str): Start date in 'dd/mm/yyyy' format. If None, no filtering is applied.
        - end (str): End date in 'dd/mm/yyyy' format. If None, no filtering is applied.
        """
        self._start_date = self.__parse_date(start)
        self._end_date = self.__parse_date(end)
        self.filter_date()


    @staticmethod
    def __parse_date(date_str):
        """
        Validate and Parse date string into datetime object.
        """
        if not date_str:
            return None
        try:
            # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html
            return pd.to_datetime(date_str, dayfirst=True)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
        

    def filter_date(self):
        """
        Filter the data by date range
        """
        # Filter the data based on the date range, if the date is out of the range, delete this row
        if self._start_date and self._end_date:
            # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.between.html
            self.data = self.original_data[self.original_data['Date_x'].between(self._start_date, self._end_date)]
        else:
            self.data = self.original_data


    def export_original_data(self):
        """
        Export the original data to a CSV file.
        """
        self.original_data.to_csv("original_data.csv")


    def additional_columns(self):
        """
        Datetime columns use for grouping and sorting
        """
        # Create a full employee label: "First Last (Employee Number)"
        self.data['Employee'] = self.data['First Name'] + ' ' + self.data['Last Name'] + ' (' + self.data[
            'Employee Number'].astype(str) + ')'
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.astype.html

        # Create a full list of Datetime columns use for grouping and sorting
        self.data['Date_x'] = pd.to_datetime(self.data['Date_x'], format='%d/%m/%Y')
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.dt.isocalendar.html
        self.data['Week'] = self.data['Date_x'].dt.isocalendar().week
        self.data['Year'] = self.data['Date_x'].dt.isocalendar().year
        self.data['Month'] = self.data['Date_x'].dt.month
        self.data['Weekday'] = self.data['Date_x'].dt.weekday
        self.data['Year_weekly'] = self.data['Year'].astype(str) + '-W' + self.data[
            'Week'].astype(str).str.zfill(2)
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.dt.strftime.html
        self.data['Year_monthly'] = self.data['Date_x'].dt.strftime('%Y-%m')
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.dt.to_period.html
        self.data['Quarter'] = self.data['Date_x'].dt.to_period('Q')


    # Reference: https://docs.python.org/3/library/typing.html#typing.Literal
    # Use Literal to restrict a variable to a specific set of string values (type hinting).
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
        
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html
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
        """
        Calculate productivity score and rank for each employee based on performance reviews and hours worked.
        """
        # Create a copy of the data for productivity analysis
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
        data_to_productivity.to_csv('employee_report.csv', index=False)

        return data_to_productivity
    

    def quarterly_performance(self):
        """
        Calculate the quarterly performance of employees based on median hours worked.
        """
        # Copy the data for quarterly performance analysis
        data_add1 = self.data.copy()

        # Group by employee and quarter, calculate median hours worked
        employee_quarterly = data_add1.groupby(['Quarter', 'Employee'])['Hours Worked'].agg(
            ['median']).reset_index()
        overall_quarterly = data_add1.groupby(['Quarter'])['Hours Worked'].agg(['median']).reset_index().rename(
            columns={'median': 'overall_median'})
        
        # Merge employee and overall quarterly data
        quarterly_performance = pd.merge(employee_quarterly, overall_quarterly, how='left', on='Quarter')

        # Calculate the difference between employee median and overall median
        quarterly_performance['diff'] = quarterly_performance['median'] - quarterly_performance['overall_median']

        # Calculate the percentage difference
        quarterly_pivot = quarterly_performance.pivot(index=['Employee'], columns='Quarter',
                                                      values='diff').reset_index().round(2)
        # save the result to a CSV file
        quarterly_pivot.to_csv('quarterly_performance.csv', index=False)

        return quarterly_pivot
    

    def weekend_compensation(self):
        """
        Calculate the weekend compensation for employees based on their hours worked.
        """
        # Copy the data for weekend compensation analysis
        data_add2 = self.data.copy()
        
        # create new column
        data_add2["IsWeekend"] = data_add2["Weekday"] >= 5

        # Find out the daily deficit for weekday
        data_add2["Weekday_Deficit"] = data_add2.apply(
            lambda row: 7.5 - row["Hours Worked"] if not row["IsWeekend"] else 0,
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