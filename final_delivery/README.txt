# Coding for Business Problems BUSA90537 Group 8
# Syndicate Assignment: employee_analysis
# Note: It is recommended to rename this file extension from `.txt` to `.md` for better and clear readability.

# Introduction
This project analyses employee worklog and performance data, summarizes working patterns, calculates overtime, employee productivity, two additional future which include quarterly performance and weekday weekend comparison, and generates insightful plots.

# File Structure
- `main.py`: Main executable python script to run analysis, generate outputs, test, and plot.
- `dataset.py`: Abstract class DataSet for loading and representing datasets, and include subclass wWorklogs and PerformanceReview.
- `clean_data.py`: Helper class for cleaning and preprocessing datasets.
- `employee_analysis.py`: Main class to load, clean, merge, and analyze employee data.
- `test.py`: Test case class inherits Unittests for validating the analysis functionality and result.
- `plot_graph.py`: Provides plotting utilities (bar chart, pie chart, line chart).
- `README.md`: Project documentation.
note: Ensure you have the following input files:
- **Input Files**: `employee_worklogs.csv`, `employee_performance_review.csv`


# How to Run and Test
## 1. Ensure you have installed required packages:
```bash
    pip install pandas matplotlib word2number numpy
```
and make sure you have following csv file under the current path:
1) employee_worklogs.csv
2) employee_performance_review.csv

## 2. Run the main script(analyser, plot):
```bash
    python main.py 
```
note: Now you have already can run the program. However, if you need, you can edit the code follow the below steps
There are three parts you can edit to run the main script as follows:

 ### 1. Analyser: How to use the EmployeeAnalyser class:
   ### analyser = EmployeeAnalyser(worklogs_file, performance_file, start_date, end_date)

   - Parameters:
     - worklogs_file: Path to worklogs csv file (e.g., "employee_worklogs.csv")
     - performance_file: Path to performance review csv file (e.g., "employee_performance_review.csv")
     - start_date: Start date for filtering (format DD/MM/YYYY)
     - end_date: End date for filtering (format DD/MM/YYYY)

   ### Available Methods:
     - summary(frequency):	Summarize 'Avg Hours Worked', 'Median Hours Worked','Min Hours Worked', 'Max Hours Worked','Number of 
                            Days Worked', frequency must choose in 'weekly', 'monthly', 'Weekday', or 'total'. Using for the question 1, 2, 6, 7, 8
     - overtime(frequency):	Calculate total overtime hours (weekly or total), frequency must choose in 'weekly', 'monthly'      
                            'Weekday', or 'total'. Using for question 3, 4
     - productivity_analysis():	Analyze productivity scores and ranks, using for question 5
     - quarterly_performance():	Compare employee performance against the company median quarterly. Using for Additional feature 1
     - weekend_compensation():	Analyze how weekend work compensates for weekday deficits. Using for Additional feature 2
     - set_dates(start=None, end=None):	Filter data by new start and end dates, which format DD/MM/YYYY. Using for Additional 
                                        feature 3 as date_filter
     - export_original_data():	Export the original unfiltered dataset

 ### 2.Plot: How to use Plotter to visualize results:
    - The Plotter class provides static methods for visualizing the results. No instance creation is needed — just call methods  directly using the class name.
    # Example:
    from plot_graph import Plotter
    
    Plotter.plot_bar(
        data=overtime,
        x_column='Employee',
        y_column='Overtime',
        title='Employee Overtime Hours',
        xlabel='Employee',
        ylabel='Total Overtime Hours',
        save_path='overtime_bar_chart'
    )
    # Parameters:
	 - data: DataFrame containing data to plot
	 - x_column: Column name for x-axis
	 - y_column: Column name for y-axis
	 - title: Title of the chart
	 - xlabel: Label for x-axis
	 - ylabel: Label for y-axis
	 - save_path: Filename to save the plot (no .png needed)

    # Plotting Features
    - **Saving Plots**: If save_path is not none, automatically saves plots as `.png`.

## 3. Run the test script:
 ### How to Run unittest:
    In python the enf of test.py wirte and run:
    ```python
        import unittest
        unittest.main(exit=False)
    ```
    or
    ```bash
        python -m unittest test.py
    ```
    You also can follow this step to change the data for test:
            # Create a test dataset
            file_worklogs = "test_employee_worklogs.csv"
            file_performance_review = "test_employee_performance_review.csv"
        and change the file_path of file_worklogs and file_performance_review


# **Key Features**:
  - Work summary reports (weekly, monthly, weekday, total), for the question 1, 2, 6, 7, 8
  - Overtime calculation, for question 3, 4
  - Productivity ranking, for question 5
  - Quarterly performance tracking, for additonal feature 1
  - Weekend compensation analysis, for additonal feature 2
  - Filter data by new start and end dates, for Additional feature 3
  - Unittest to test the result
  - Auto-generated plots by calling the static method directly through the Plotter class


# Expected ouput file
| No. | Filename                    | Remarks     | Content |
|:---:|:-----------------------------|:-----------:|:--------|
| 1   | employee report              | Basic       | For Q5, the performance metrics determining the most productive employee |
| 2   | original data                | Others      | The combined, filtered data that is used for analysis |
| 3   | overtime_total               | Basic       | For Q3, the total amount of hours worked overtime |
| 4   | overtime_week                | Basic       | For Q4, the amount of hours worked overtime per week |
| 5   | quarterly_performance        | Additional  | Additional Feature 1, calculating the deviance of the employees from the mean |
| 6   | summary_monthly              | Basic       | For Q2 and 8, calculating the monthly average hours worked as well as the monthly summary for the employee |
| 7   | summary_total                | Basic       | For Q6, the total amount of hours worked |
| 8   | summary_weekly               | Basic       | For Q1 and 7, calculating the weekly average hours worked as well as the weekly summary for the employee |
| 9   | weekday weekday comparison   | Additional  | Additional Feature 2, calculating the weekly deficit in hours worked and compare with weekend work hours |
| 10  | employee_weekly_deficit_vs_compensation.png | Additional | Visualization of weekday vs weekend work patterns       |
| 11  | individual_workhour_deviation.png        | Additional | Visualization of quarterly workhour deviation 

# Reference list
1. https://pandas.pydata.org/docs/
2. https://docs.python.org/3/library/abc.html#abc.ABC
3. https://pypi.org/project/word2number/
4. https://docs.python.org/3/library/typing.html#typing.Literal
5. https://matplotlib.org/stable/gallery/index.html
6. https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray
7. https://docs.python.org/3/library/re.html#re.match
8. https://docs.python.org/3/library/typing.html#typing.Union
9. https://docs.python.org/3/tutorial/classes.html#private-variables
10. https://docs.python.org/3/library/functions.html#staticmethod
11. https://docs.python.org/3/reference/datamodel.html#object.__add__


## Now you are ready to run the analysis and visualize the results with just a few lines of code!!!