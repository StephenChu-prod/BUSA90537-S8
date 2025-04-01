from datetime import date
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference, Series, ScatterChart, LineChart, StockChart, AreaChart, AreaChart3D
from openpyxl.utils.dataframe import dataframe_to_rows

def quarterly_function(date):
    if date.month <= 3:
        flag = "Q1"
    elif date.month <= 6:
        flag = "Q2"
    elif date.month <= 9:
        flag = "Q3"
    else:
        flag = "Q4"

    return flag

def quarterly_performance(data):
    data['quarter'] = pd.to_datetime(data['Date_x'], format='%Y-%m-%d').apply(quarterly_function)
    data['year'] = pd.to_datetime(data['Date_x'], format='%Y-%m-%d').dt.strftime('%Y')
    data['year-quarter'] = data["year"] + " - " + data['quarter']
    employee_quarterly = data.groupby(['year-quarter', 'Employee Number'])['Hours Worked'].agg(['median']).reset_index()
    overall_quarterly = data.groupby(['year-quarter'])['Hours Worked'].agg(['median']).reset_index().rename(columns={'median': 'overall_median'})
    quarterly_performance = pd.merge(employee_quarterly, overall_quarterly, how='left', on='year-quarter')
    quarterly_performance['diff'] = quarterly_performance['median'] - quarterly_performance['overall_median']
    quarterly_pivot = quarterly_performance.pivot(index=['Employee Number'], columns='year-quarter',values='diff').reset_index()  # .drop(columns='Employee Number')
    quarterly_pivot.columns.name = None


def excel_chart(data):
    df = quarterly_performance(data)

    wb = Workbook()
    ws = wb.active

    rows = dataframe_to_rows(df, index=False, header=True)

    for r_idx, row in enumerate(rows, 1):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    # Define data and categories
    num_rows = df.shape[0] + 1  # include header
    num_cols = df.shape[1]

    data = Reference(ws, min_col=2, min_row=1, max_col=num_cols, max_row=num_rows)
    categories = Reference(ws, min_col=1, min_row=2, max_row=num_rows)

    # Create clustered bar chart
    chart = BarChart()
    chart.type = "col"
    chart.grouping = "clustered"
    chart.title = "Employee Work Hour Deviation by Quarter"
    chart.y_axis.title = "Hour Deviation"
    chart.x_axis.title = "Quarter"

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)

    # Position the chart
    ws.add_chart(chart, "H2")

    # Save workbook
    wb.save("employee_hour_deviation_chart.xlsx")


