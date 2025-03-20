import pandas as pd
from datetime import datetime, timedelta

# Read the data (update the path to where your file is located)
data = pd.read_csv('output_CleanData.csv')

# Convert date to datetime format
data['Date_x'] = pd.to_datetime(data['Date_x'])

# Add week column
data['Week'] = data['Date_x'].dt.strftime('%Y-%U')

# Group by employee and week, sum hours worked
weekly_totals = data.groupby(['Employee Number', 'First Name', 'Last Name', 'Week'])['Hours Worked'].sum().reset_index()

# Round hours to 1 decimal place
weekly_totals['Hours Worked'] = weekly_totals['Hours Worked'].round(1)

# Export to CSV
weekly_totals.to_csv('weekly_hours.csv', index=False)

print(f"Weekly totals for {weekly_totals['Employee Number'].nunique()} employees exported to weekly_hours.csv")
print("\nSample of results:")
print(weekly_totals.head())