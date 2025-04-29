import pandas as pd
from word2number import w2n


class DataCleaner:
    def __init__(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def replace_number_words(self):
        """
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

    def correct_name(self):
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

    def valid_date(self):
        """
        Filter the data by date range
        """
        self._data["Date"] = pd.to_datetime(self._data["Date"], format="mixed", errors="coerce")
