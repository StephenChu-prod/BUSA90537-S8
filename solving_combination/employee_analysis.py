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
import unittest

class DataSet(ABC):
    @abstractmethod
    def read_csv_file(self, file):
        """
        The function that read the contain from CSV file

        Input: The file path -> string
        Output: The contains of CSV file -> dataframe
        """
        data = pd.read_csv(file)
        return data
    
    @abstractmethod
    def clean_data(self, data):
        pass


class Worklogs(DataSet):
    def __init__(self, file):
        self.data_worklogs = self.read_csv_file(file)
        self.data_worklogs = self.clean_data(self.data_worklogs)

    def read_csv_file(self, file):
        data = pd.read_csv(file)
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
    
    def fix_date(self, date):
        """
        Change the date so that it can fit into the range
        """
        if date.month in (11,12) and date.year != 2024:
            return date.replace(year=2024)
        elif date.month in (1,2) and date.year != 2025:
            return date.replace(year=2025)
        return date
    
    def correct_row(self, row, reference):
        """
        Correct the invaild name or null name, make it match the employee number in reference
        """
        emp_id = row["Employee Number"]
        if emp_id in reference.index:
            correct_name = reference.loc[emp_id]
            if row["First Name"] != correct_name["First Name"] or row["Last Name"] != correct_name["Last Name"]:
                row["First Name"] = correct_name["First Name"]
                row["Last Name"] = correct_name["Last Name"]
        return row


    def clean_data(self, data_worklogs):
        """
        Clean and preprocess the data.

        Part 1: Modify 'Hours Worked', replacing words with numbers.
        Part 2: Convert 'Date' column to datetime format and remove invalid rows.
        Part 3: Check the employee name and employee number
        """
        # Identify and replace invalid numbers in Hours Worked
        not_numeric = pd.to_numeric(data_worklogs['Hours Worked'], errors='coerce').isnull()
        data_worklogs.loc[not_numeric, 'Hours Worked'] = data_worklogs.loc[not_numeric, 'Hours Worked'].apply(self.replace_number_words)

        # Identify and replace invalid value in Date Column
        data_worklogs["Date"] = pd.to_datetime(data_worklogs["Date"], format="mixed", errors="coerce")
        
        # Fix the wrong dates
        data_worklogs['Date'] = pd.to_datetime(data_worklogs['Date'], format='mixed').apply(self.fix_date) 

        # Filter the data out of range 
        start_date = data_worklogs["Date"].min()
        end_date = data_worklogs["Date"].max()  
        data_worklogs = data_worklogs[data_worklogs['Date'].between(start_date, end_date)] 

        # Dataframe name saved the column include emplyoee name and number
        name = pd.DataFrame(data_worklogs, columns=["Employee Number", "First Name", "Last Name"])

        # Reference is used as standard to correct the name
        reference = (
        name[name["Last Name"] != ""].drop_duplicates(subset="Employee Number", keep="first")
        .set_index("Employee Number")[["First Name", "Last Name"]]
        )

        # Correct the invaild name or null name
        data_worklogs = data_worklogs.apply(lambda row: self.correct_row(row, reference), axis=1)

        return data_worklogs
        
    
class PerformanceReview(DataSet):
    def __init__(self, file):
        self.data_performance_review = self.read_csv_file(file)

    def read_csv_file(self, file):
        data = pd.read_csv(file)
        return data
    
    def clean_data(self):
        pass


if __name__ == '__main__':
    file_worklogs = "/Users/chustephen/E/MBusA/Module2/CodingforBusinessProblems/GitHub/BUSA90537-S8/employee_worklogs.csv"
    file_performance_review = "/Users/chustephen/E/MBusA/Module2/CodingforBusinessProblems/GitHub/BUSA90537-S8/employee_performance_review.csv"
    worklogs = Worklogs(file_worklogs)
    performance_review = PerformanceReview(file_performance_review)
    worklogs.data_worklogs.to_csv('data_clean.csv', index=False)
              
        



