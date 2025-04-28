from employee_analyser import EmployeeAnalyser
from test import TestAnalyser
import unittest
from plot_graph import Plotter

if __name__ == '__main__':
    # Define the file path and timeframe here
    file_worklogs = "employee_worklogs.csv"
    file_performance_review = "employee_performance_review.csv"
    start_date = "04/11/2024"
    end_date = "10/02/2025"

    # Run the program here
    analyser = EmployeeAnalyser(file_worklogs, file_performance_review,\
                                 start_date=start_date, end_date=end_date)
    analyser.summary(frequency='weekly')

    # Question 1 and 7
    analyser.summary(frequency='weekly')
    analyser.summary(frequency='Weekday')
    analyser.summary(frequency='total')
    
    # Question 2 and 8
    analyser.summary(frequency='monthly')
    
    # Question 3 and 4
    analyser.overtime(frequency='weekly')
    overtime = analyser.overtime(frequency='total')

    # Question 5 and 6
    productivity = analyser.productivity_analysis()

    # additional features
    quarterly_performance = analyser.quarterly_performance()
    compensation = analyser.weekend_compensation()
    analyser.set_dates()  # if no parameter then reset to original (no filtering) -> no output, just filtering
    analyser.export_original_data()
 
    # test the analyser
    unittest.main(exit=False)

    # Plot overtime
    Plotter.plot_bar(
        data=overtime,
        x_column='Employee',
        y_column='Overtime',
        title='Employee Overtime Hours',
        xlabel='Employee',
        ylabel='Total Overtime Hours',
        save_path='overtime_bar_chart'
    )

    # Plot productivity rank
    Plotter.plot_bar(
        data=productivity,
        x_column='Employee',
        y_column='productivity_rank',
        title='Employee Productivity Rank',
        xlabel='Employee',
        ylabel='Productivity Rank',
        save_path='productivity_rank_bar_chart'
    )


    # Plot quarterly performance for 2024Q4
    quarterly_performance.columns = quarterly_performance.columns.map(str)
    Plotter.plot_bar(
        data=quarterly_performance,
        x_column='Employee',
        y_column='2024Q4',
        title='Individual Workhour Deviation from Team Average (2024Q4)',
        xlabel='Employee',
        ylabel='Hours',
        save_path='2024Q4_workhour_deviation_bar_chart',
        clr='green'
    )

    # Plot quarterly performance for 2025Q1
    Plotter.plot_bar(
        data=quarterly_performance,
        x_column='Employee',
        y_column='2025Q1',
        title='Individual Workhour Deviation from Team Average (2025Q1)',
        xlabel='Employee',
        ylabel='Hours',
        save_path='2025Q1_workhour_deviation_bar_chart',
        clr='blue'
    )

