import pandas as pd
from abc import ABC, abstractmethod
from word2number import w2n
import csv
import unittest
from typing import Literal
from Dataset import *


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
        self.data['Year_week'] = self.data['Year'].astype(str) + '-W' + self.data[
            'Week'].astype(str).str.zfill(2)
        self.data['Year_month'] = self.data['Date_x'].dt.strftime('%Y-%m')
        self.data['Quarter'] = self.data['Date_x'].dt.to_period('Q')

    def summary(self, frequency: Literal['weekly', 'monthly', 'weekday', 'total'] = 'weekly'):
        """
        Generate a summary based on the specified frequency and pivot option.

        Parameters:
        - frequency (Literal['weekly', 'monthly', 'weekday']): The time frequency for grouping data.
            Options are 'weekly', 'monthly','weekday'. Default is 'weekly'.

        Returns:
        - Summary data grouped by the specified frequency.
        """

        df = self.data.copy()
        if frequency == 'weekly':
            index_col = ['Year_week', 'Employee']
        elif frequency == 'monthly':
            index_col = ['Year_month', 'Employee']
        elif frequency == 'weekday':
            index_col = ['Weekday', 'Employee']
        elif frequency == 'total':
            index_col = ['Employee']

        grouped = df.groupby(index_col)['Hours Worked'].agg(
            ['mean', 'median', 'min', 'max', 'count'])
        grouped.columns = ['Avg Hours Worked', 'Median Hours Worked',
                           'Min Hours Worked', 'Max Hours Worked','Number of Days Worked']
        grouped = grouped.round(2).reset_index()
        grouped.to_csv(f'grouped_summary_{frequency}.csv', index=False)

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

        # Export to CSV
        grouped.to_csv('total_overtime.csv')

    def productivity_analysis(self):
        df = self.data.copy()

        # Extract performance score from reviews
        df['Performance Score'] = df['Performance Review'].str.extract(r'(\d)').astype(int)

        # Group by employee and performance score, calculate median hours and entry count
        df = df.groupby(['Employee', 'Performance Score'])['Hours Worked'].agg(
            ['median', 'count']).reset_index()

        # Calculate the maximum days worked across all employees
        max_days = df['count'].max()

        # Calculate days missed penalty
        df['days_missed_penalty'] = (max_days - df['count']) / max_days

        # Calculate Adjusted Efficiency
        df['productivity_score'] = df['Performance Score'] / (df['median'] * (1 + df['days_missed_penalty'])) * 100

        # Assign rank based on Adjusted Efficiency (higher is better)
        df['productivity_rank'] = df['productivity_score'].rank(ascending=False, method='dense').astype(int)

        df = df[['Employee', 'productivity_score', 'productivity_rank']].round(2)
        # Save results
        df.to_csv('productivity_analysis.csv', index=False)

    def quarterly_performance(self):
        data = self.data.copy()

        employee_quarterly = data.groupby(['Quarter', 'Employee'])['Hours Worked'].agg(
            ['median']).reset_index()
        overall_quarterly = data.groupby(['Quarter'])['Hours Worked'].agg(['median']).reset_index().rename(
            columns={'median': 'overall_median'})
        quarterly_performance = pd.merge(employee_quarterly, overall_quarterly, how='left', on='Quarter')
        quarterly_performance['diff'] = quarterly_performance['median'] - quarterly_performance['overall_median']
        quarterly_pivot = quarterly_performance.pivot(index=['Employee'], columns='Quarter',
                                                      values='diff').reset_index().round(2)
        quarterly_pivot.to_csv('quarterly_performance.csv', index=False)

    def weekend_compensation(self):
        """
        This method computes how well each employee’s weekend work “makes up” for any shortfall in their weekday hours,
        then compares that with their performance score
        """

        df = self.data.copy()
        # create new column
        df["IsWeekend"] = df["Weekday"] >= 5

        # Find out the daily deficit for weekday
        df["Weekday_Deficit"] = df.apply(
            lambda row: max(0, 7.5 - row["Hours Worked"]) if not row["IsWeekend"] else 0,
            axis=1
        )

        # separate the weekday hours from weekend
        df["Weekend_Hours"] = df.apply(
            lambda row: row["Hours Worked"] if row["IsWeekend"] else 0,
            axis=1
        )

        # Group by weekly
        weekly = df.groupby(["Employee", "Year_week"]).agg(Total_Weekday_Deficit=("Weekday_Deficit", "sum"),
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
        employee_score = df[["Employee", "Performance Review"]].drop_duplicates(subset="Employee")
        agg = pd.merge(agg, employee_score, on="Employee", how="left")

        agg = agg.round(2)
        # Reset index for a table
        result = agg.reset_index().drop(columns=["index"])

        result.to_csv('weekend_compensation.csv', index=False)
