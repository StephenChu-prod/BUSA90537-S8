import numpy as np
import pandas as pd



def replace_number_words(text):
    """
    Helper function that converts words to numbers

    Input: String
    Output: Integer
    """
    text = str(text).lower()  # Convert to lowercase to handle case-insensitivity
    if text == 'zero':
        return 0
    elif text == 'one':
        return 1
    elif text == 'two':
        return 2
    elif text == 'three':
        return 3
    elif text == 'four':
        return 4
    elif text == 'five':
        return 5
    elif text == 'six':
        return 6
    elif text == 'seven':
        return 7
    elif text == 'eight':
        return 8
    elif text == 'nine':
        return 9
    elif text == 'ten':
        return 10
    else:
        return 0  # Return the original value if not a recognized number word

def fix_date(date):
    """
    Change the date so that it can fit into the range
    """

    if date.month in (11,12) and date.year != 2024:
        return date.replace(year=2024)
    elif date.month in (1,2) and date.year != 2025:
        return date.replace(year=2025)
    return date

def clean_data(file):
    """Clean and preprocess the data.

    Part 1: Modify 'Hours Worked', replacing words with numbers.
    Part 2: Convert 'Date' column to datetime format and remove invalid rows.
    """
    # Identify and replace invalid numbers in Hours Worked
    not_numeric = pd.to_numeric(file['Hours Worked'], errors='coerce').isnull()
    file.loc[not_numeric, 'Hours Worked'] = file.loc[not_numeric, 'Hours Worked'].apply(replace_number_words)

    # Defining the range of Date Column
    start_date = pd.to_datetime('04/11/2024', format='%d/%m/%Y')
    end_date = pd.to_datetime('10/02/2025', format='%d/%m/%Y')

    # Convert into Datetime Format and Filter Date
    file['Date'] = pd.to_datetime(file['Date'], format='mixed').apply(fix_date)     # Fix the wrong dates
    clean_file = file[file['Date'].between(start_date, end_date)]   # Filter the data out of range
    return clean_file


def overtime(hours):
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


def total_overtime_each(df):
    df['Daily Overtime Each Employee'] = df['Hours Worked'].apply(overtime)
    df['Total Overtime Each Employee'] = \
        df.groupby('Employee Number')[['Daily Overtime Each Employee']].transform('sum')
    return df


def week_number(df):
    """
    Define the day of week and week number
    """
    df['Weekday'] = df['Date'].dt.strftime('%A')
    start_date = pd.to_datetime('04/11/2024', format='%d/%m/%Y')
    df['Week Number'] = ((df['Date'] - start_date).dt.days // 7) + 1
    return df

def total_weekly_overtime_each(df):
    df['Total Weekly Overtime Each Employee'] = \
        df.groupby(['Employee Number','Week Number'])[['Daily Overtime Each Employee']].transform('sum')
    return df


if __name__ == '__main__':
    employee_performance_review = pd.read_csv(r"C:\Users\76566\Desktop\files for assignment\employee_performance_review.csv")
    employee_worklogs = pd.read_csv(r"C:\Users\76566\Desktop\files for assignment\employee_worklogs.csv")
    data = clean_data(employee_worklogs)
    data = total_overtime_each(data)        # For Question 3
    data = week_number(data)                # 看看能不能把这个加到data clean 中
    data = total_weekly_overtime_each(data) # For Question 4
    merged_df = pd.merge(data, employee_performance_review, on='Employee Number')
    merged_df.to_csv(r"output_CleanData.csv", index=False)