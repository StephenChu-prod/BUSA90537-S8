"""
Implement a non-trivial program employee_analysis.py in Python to complete:

1. Read work logs from CSV files. Ensure that any data are inconsistencies.

2. Process data from 4 November 2024 until 10 of February 2025 and analyse employees’ productivity.

3. Produce weekly and monthly productivity reports based on provided CSV files.

4. Export the results to employee_report.csv file.

5. Extensive test code used to develop the program.
"""

import pandas as pd
from abc import ABC, abstractmethod
from word2number import w2n
import csv
import unittest

class DataSet(ABC):
    @abstractmethod
    def read_csv_file(self, file):
        """
        The function that read the contain from CSV file

        Input: The file path -> string
        Output: The contains of CSV file -> dataframe
        """
        with open(file, 'r') as csvfile:
            # Use the csv module to read the file
            reader = csv.reader(csvfile)
            # Read the records into a list
            records = list(reader)
            # Create a DataFrame from the records
            data = pd.DataFrame(records[1:], columns=records[0])
        return data
    
    @abstractmethod
    def clean_data(self, data):
        pass


class Worklogs(DataSet):
    def __init__(self, file, start_date = None, end_date = None):
        """
        The constructor of Worklogs class
        Input: The file path -> DataFrame
        """
        self.data_worklogs = self.read_csv_file(file)
        self.data_worklogs = self.clean_data(self.data_worklogs, start_date, end_date)

    def read_csv_file(self, file):
        with open(file, 'r') as csvfile:
            # Use the csv module to read the file
            reader = csv.reader(csvfile)
            # Read the records into a list
            records = list(reader)
            # Create a DataFrame from the records
            data = pd.DataFrame(records[1:], columns=records[0])
        return data

    def replace_number_words(self, text):
        """
        Helper function that converts numbers to words

        Input: String
        Output: Integer
        """
        # try parse the word to number and convert to lowercase to handle case-insensitivity
        try:
            return w2n.word_to_num(str(text).lower())
        except:
        # # Return the original value if not a recognized number word
            return text
    
    
    def correct_name(self, data_worklogs):
        """
        Correct the invaild name or null name, make it match the employee number in reference
        """
        # Dataframe name saved the column include emplyoee name and number
        name = pd.DataFrame(data_worklogs, columns=["Employee Number", "First Name", "Last Name"])

        # Reference is used as standard to correct the name
        reference = (
        name[name["Last Name"] != ""].drop_duplicates(subset="Employee Number", keep="first")
        .set_index("Employee Number")[["First Name", "Last Name"]]
        )

        # Correct the invaild name or null name
        data_worklogs = data_worklogs.apply(lambda row: self.correct_name_row(row, reference), axis=1)

        return data_worklogs
    
        
    def correct_name_row(self, row, reference):
        """
        Helper function to correct the name of each row
        """
        employee_number = row["Employee Number"]
        if employee_number in reference.index:
            row["First Name"] = reference.loc[employee_number, "First Name"]
            row["Last Name"] = reference.loc[employee_number, "Last Name"]
        return row
    
    
    def date_filter(self, data_worklogs, start_date, end_date):
        """
        Filter the data by date range
        """
        if start_date is not None:
            # Convert the start_date to datetime
            start_date = pd.to_datetime(start_date, format="mixed", errors="coerce")
        else:
            start_date = data_worklogs["Date"].min()
            print("You did not specify the start date to filter csv file, some dates may be out of range!!!")

        if end_date is None:
            end_date = data_worklogs["Date"].max()  
            print("You did not specify the end date to filter csv file, some dates may be out of range!!!")
        else:
            # Convert the end_date to datetime
            end_date = pd.to_datetime(end_date, format="mixed", errors="coerce")

        # Filter the data based on the date range, if the date is out of the range, delete this row
        data_worklogs = data_worklogs[data_worklogs['Date'].between(start_date, end_date)] 

        return data_worklogs
    

    def clean_data(self, data_worklogs, start_date, end_date):
        """
        Clean and preprocess the data.

        Part 1: Modify 'Hours Worked', replacing words with numbers.
        Part 2: Convert 'Date' column to datetime format and remove invalid rows.
        part 3: Filte the data by date range
        Part 4: Check the employee name and employee number
        """
        # Identify and replace invalid numbers in Hours Worked
        not_numeric = pd.to_numeric(data_worklogs['Hours Worked'], errors='coerce').isnull()
        data_worklogs.loc[not_numeric, 'Hours Worked'] = data_worklogs.loc[not_numeric, 'Hours Worked'].apply(self.replace_number_words)

        # Identify and replace invalid value in Date Column
        data_worklogs["Date"] = pd.to_datetime(data_worklogs["Date"], format="mixed", errors="coerce")

        # Filter the data out of range
        data_worklogs = self.date_filter(data_worklogs, start_date, end_date) 

        # Correct the invalid name or null name
        data_worklogs = self.correct_name(data_worklogs)

        return data_worklogs
        
    
class PerformanceReview(DataSet):
    def __init__(self, file):
        self.data_performance_review = self.read_csv_file(file)

    def read_csv_file(self, file):
        with open(file, 'r') as csvfile:
            # Use the csv module to read the file
            reader = csv.reader(csvfile)
            # Read the records into a list
            records = list(reader)
            # Create a DataFrame from the records
            data = pd.DataFrame(records[1:], columns=records[0])
        return data
    
    def clean_data(self):
        pass


if __name__ == '__main__':
    file_worklogs = "/Users/chustephen/E/MBusA/Module2/CodingforBusinessProblems/GitHub/BUSA90537-S8/employee_worklogs.csv"
    file_performance_review = "/Users/chustephen/E/MBusA/Module2/CodingforBusinessProblems/GitHub/BUSA90537-S8/employee_performance_review.csv"
    worklogs = Worklogs(file_worklogs, start_date="2024-11-04", end_date="2025-02-10")
    performance_review = PerformanceReview(file_performance_review)
    worklogs.data_worklogs.to_csv('data_clean_1.csv', index=False)
              
        



