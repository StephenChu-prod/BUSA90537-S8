import pandas as pd

# Read the data
data = pd.read_csv('output_CleanData.csv')

# Convert date to datetime format
data['Date_x'] = pd.to_datetime(data['Date_x'])

# Add month column
data['Month'] = data['Date_x'].dt.strftime('%Y-%m')

# Group by employee and month, sum hours worked
monthly_totals = data.groupby(['Employee Number', 'First Name', 'Last Name', 'Month'])['Hours Worked'].sum().reset_index()

# Add months name for readability
month_map = {
    '2024-11': 'November 2024',
    '2024-12': 'December 2024',
    '2025-01': 'January 2025',
    '2025-02': 'February 2025'
}
monthly_totals['Month Name'] = monthly_totals['Month'].map(month_map)

# Round hours to 1 decimal place
monthly_totals['Hours Worked'] = monthly_totals['Hours Worked'].round(1)

# Export to CSV
monthly_totals.to_csv('monthly_hours.csv', index=False)

print(f"Monthly totals for {monthly_totals['Employee Number'].nunique()} employees exported to monthly_hours.csv")
print("\nTotal hours worked per month:")
print(monthly_totals.head())