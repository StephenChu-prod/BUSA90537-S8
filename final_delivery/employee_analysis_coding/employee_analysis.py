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
    analyser = EmployeeAnalyser(file_worklogs, file_performance_review,start_date=start_date, end_date=end_date)

    # Question 1 and 7
    analyser.summary(frequency='weekly')
    # analyser.summary(frequency='Weekday')
    analyser.summary(frequency='total')
    analyser.summary(frequency='weekly')
    
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

    # Before plotting, adjust the data
    compensation_plot = compensation.copy()
    compensation_plot['Total_Weekday_Deficit'] *= -1

    # Now call your Plotter
    Plotter.plot_stacked_bar(
        data=compensation_plot,
        x_column='Employee',  
        y_columns=['Total_Weekday_Deficit', 'Total_Weekend_Hours'],  
        title='Employee Weekly Workhour Deficit vs Weekend Compensation',
        xlabel='Employee and Week',  
        ylabel='Hours',
        save_path='employee_weekly_deficit_vs_compensation'
    )

    # Create a new dataframe for plotting
    deviation_plot = quarterly_performance.copy()

    # Now call your new Plotter method
    Plotter.plot_grouped_bar(
        data=deviation_plot,
        x_column='Employee',
        y_columns=['2024Q4', '2025Q1'],
        title='Individual Workhour Deviation from Team Average (Q4 vs Q1)',
        xlabel='Employee',
        ylabel='Deviation from Team Median (hours)',
        colors=['#5DADE2', '#E74C3C'],
        save_path='individual_workhour_deviation'
    )

    
    # test the analyser
    # unittest.main(exit=False)
