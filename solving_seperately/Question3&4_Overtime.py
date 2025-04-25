def overtime(hours):
    """
    Helper function that converts words to numbers and filters numbers
    Input: String
    Output: Integer
    """
    hours = float(hours)
    if hours > 7.5:
        return hours - 7.5
    else:
        return 0


def total_overtime_each(df):
    df['Daily Overtime Each Employee'] = df['Hours Worked'].apply(overtime)
    df['Total Overtime Each Employee'] = \
        df.groupby('Employee Number')[['Daily Overtime Each Employee']].transform('sum')
    return df


def week_number(df):
    """
    Define the day of week and week number
    """
    df['Weekday'] = df['Date'].dt.strftime('%A')
    start_date = pd.to_datetime('04/11/2024', format='%d/%m/%Y')
    df['Week Number'] = ((df['Date'] - start_date).dt.days // 7) + 1
    return df

def total_weekly_overtime_each(df):
    df['Total Weekly Overtime Each Employee'] = \
        df.groupby(['Employee Number','Week Number'])[['Daily Overtime Each Employee']].transform('sum')
    return df


if __name__ == '__main__':
    employee_performance_review = \
    pd.read_csv(r"C:\Users\76566\Desktop\files for assignment\employee_performance_review.csv")
    employee_worklogs = pd.read_csv(r"C:\Users\76566\Desktop\files for assignment\employee_worklogs.csv")
    data = total_overtime_each(data)        # For Question 3
    data = week_number(data)
    data = total_weekly_overtime_each(data) # For Question 4