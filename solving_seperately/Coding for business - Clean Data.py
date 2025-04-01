import pandas as pd
import numpy as np

def replace_number_words(text):
    """
    Helper function that converts numbers to words

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

def calculation(file):
    pass

if __name__ == '__main__':
    employee_worklogs = "employee_worklogs.csv"   # Enter your file name here
    employee_performance_review = pd.read_csv("employee_performance_review.csv")
    worklongs_data = pd.read_csv(employee_worklogs)
    data = clean_data(worklongs_data)
    merged_df = pd.merge(data, employee_performance_review, on='Employee Number')
    merged_df.to_csv(r"output_CleanData.csv", index=False)
