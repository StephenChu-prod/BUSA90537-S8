from EmployeeAnalyser import EmployeeAnalyser


if __name__ == '__main__':
    """
    Main function: Run the program here
    """

    # Define the file path and timeframe here
    file_worklogs = "employee_worklogs.csv"
    file_performance_review = "employee_performance_review.csv"
    start_date = "04/11/2024"
    end_date = "10/02/2025"

    # Run the program here
    analyser = EmployeeAnalyser(file_worklogs, file_performance_review, start_date=start_date, end_date=end_date)

    # This is the original data for making all the analysis
    analyser.export_original_data()

    # Question 1 and 7
    analyser.summary(frequency='weekly')
    analyser.summary(frequency='monthly')
    analyser.summary(frequency='weekday')
    analyser.summary(frequency='total')

    # Question 2 and 8
    analyser.summary(frequency='monthly')

    # Question 3 and 4
    analyser.total_overtime()

    # Question 5 and 6
    analyser.productivity_analysis()

    # additional features
    analyser.quarterly_performance()
    analyser.weekend_compensation()
    analyser.set_dates()  # if no parameter then reset to original (no filtering)