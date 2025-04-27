import pandas as pd # Reference: https://pandas.pydata.org/docs/
from abc import ABC, abstractmethod # Reference: https://docs.python.org/3/library/abc.html#abc.ABC
import csv
from clean_data import DataCleaner

class DataSet(ABC):
    def __init__(self, source):
        """Initialize dataset with source and optional date range."""
        # Reference: https://docs.python.org/3/library/typing.html#typing.Union
        # Use | for type hinting in Python 3.10+
        # Reference: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
        self._data: pd.DataFrame | None = None 

        # Double underscore methods like __parse_date are subject to name mangling and are private methods.
        # This means that they are not accessible from outside the class using the name __parse_date.
        # Reference: https://docs.python.org/3/tutorial/classes.html#private-variables
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
        The @staticmethod decorator is used to define a method that belongs to the class
        but does not require an instance (self) to be called.
        reference: https://docs.python.org/3/library/functions.html#staticmethod
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
        """
        Merge two datasets on Employee Number.
    
        Magic method: override the `+` operator for DataSet objects.
        Reference: https://docs.python.org/3/reference/datamodel.html#object.__add__
        """
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
        """
        All the cleaning and preprocessing are carried out by subclasses.
        Abstract method: subclasses must implement this method.
        Reference: https://docs.python.org/3/library/abc.html#abc.abstractmethod
        """
        pass


class Worklogs(DataSet):
    """
    Class for worklogs dataset.
    Inherits from DataSet.
    """

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

        # 3. Correct the invalid name or null name
        cleaner.correct_name()

        self._data = cleaner.get_data()


class PerformanceReview(DataSet):
    """
    Class for performance review dataset.
    Inherits from DataSet.
    """
    def __init__(self, file):
        super().__init__(file)

    def clean_data(self):
        pass