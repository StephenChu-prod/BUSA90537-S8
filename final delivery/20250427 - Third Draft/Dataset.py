import pandas as pd
from abc import ABC, abstractmethod
import csv
from Cleandata import DataCleaner


class DataSet(ABC):
    """
    The abstract class that define the function that will be used in the child class
    """

    def __init__(self, source):
        """Initialize dataset with source and optional date range."""
        self._data = None
        self.__load_data(source)

    def get_dataset(self):
        """Return the processed dataset."""
        return self._data



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
    def __init__(self, file):
        """The constructor of Worklogs class"""
        super().__init__(file)

    def clean_data(self):
        """
        Clean and preprocess the data.
        Part 1: Convert 'Date' column to datetime format and remove invalid rows.
        Part 2: Modify 'Hours Worked', replacing words with numbers.
        Part 3: Check the employee name and employee number
        """

        # Create a cleaner object, use cleaner to clean data
        cleaner = DataCleaner(self._data)

        # 1. Identify and replace invalid value in Date Column
        cleaner.valid_date()

        # 2. change words to numbers
        cleaner.replace_number_words()

        # 4. Correct the invalid name or null name
        cleaner.correct_name()

        self._data = cleaner.get_data()


class PerformanceReview(DataSet):
    def __init__(self, file):
        super().__init__(file)

    def clean_data(self):
        cleaner = DataCleaner(self._data)
        cleaner.valid_date()
        self._data = cleaner.get_data()
