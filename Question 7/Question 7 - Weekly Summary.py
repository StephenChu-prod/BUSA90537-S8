import numpy as np
import pandas as pd


def add_date_column(df):
    """
    Generate new Datetime columns use for grouping and sorting

    input: merged_df - with 'Date_x'
    output: merged_df with extra datetime columns
    """
    assert 'Date_x' in df.columns, '"Date_x" Column is missing in DateFrame'

    df['Date_x'] = pd.to_datetime(df['Date_x'], format='%d/%m/%Y')
    df['Week'] = df['Date_x'].dt.isocalendar().week
    df['Year'] = df['Date_x'].dt.isocalendar().year
    df['Month'] = df['Date_x'].dt.month
    df['Weekday'] = df['Date_x'].dt.weekday
    return df


def weekly_summary(df):
    """
    Generate a weekly summary of hours worked per employee and overall average across all employees.

    input: cleaned df - with at least 'Week', 'Year' columns
    output: weekly summary - mean(self), mean(all employees),median, min, max, std on Hours Worked
    """

    # Check if all the necessary columns are in the dataframe
    assert all(col in df.columns for col in ['Week', 'Year',
                                             'Hours Worked']), "'Week', 'Year', 'Year_week', 'Hours Worked' are required in the DataFrame"

    # Check if the dataframe columns are correctly formatted
    df['Hours Worked'] = pd.to_numeric(df['Hours Worked'], errors='coerce')

    # Generate weekly summary for individual employees
    summary = df.groupby(['Employee Number', 'Year', 'Week'])['Hours Worked'].agg(
        ['mean', 'median', 'min', 'max']).reset_index()
    summary.columns = ['Employee Number', 'Year', 'Week', 'Avg Hours', 'Median Hours', 'Min Hours', 'Max Hours']
    summary['Year_Week'] = summary['Year'].astype(str) + '-W' + summary['Week'].astype(str).str.zfill(2)

    # Generate Weekly summary across all employees
    summary_weekly = df.groupby(['Year', 'Week'])['Hours Worked'].agg(['mean']).reset_index()
    summary_weekly.columns = ['Year', 'Week', 'Avg Hours (All Employees)']
    summary_weekly['Year_Week'] = summary_weekly['Year'].astype(str) + '-W' + summary_weekly['Week'].astype(
        str).str.zfill(2)

    # Merge summary and sort by Date
    merged_summary = pd.merge(summary, summary_weekly, on=['Year', 'Week', 'Year_Week'])
    merged_summary = merged_summary.sort_values(by=['Year', 'Week'])

    # Drop Year and Date Columns
    merged_summary = merged_summary.drop(columns=['Year', 'Week'])

    return merged_summary


if __name__ == '__main__':
    employee_worklogs = pd.read_csv("sample.csv")  # Enter your file name here
    df = add_date_column(employee_worklogs)
    df = weekly_summary(df)
    print(df.head())
