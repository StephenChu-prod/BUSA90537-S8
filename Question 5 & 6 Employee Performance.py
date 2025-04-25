
def productive_employee(df):
    '''
    Most productive employee is determined by 3 metrics (from most priority to least):
    (1) Performance Review result (5: most productive, 1: least productive)
    (2) Median of work hours (lower median : higher productivity)
    (3) Count of workday (higher count of workday : higher productivity)
    '''
    df = df.groupby(['Employee Number','Performance Review'])['Hours Worked'].agg(['median','count']).reset_index()
    # Compute the 7-day rolling average per employee
    df.sort_values(by = ['Performance Review','median','count'], ascending = [False,True,False]).reset_index(drop=True)
    return df

def total_worked_hours(df):
    df = df.groupby('Employee Number')['Hours Worked'].agg(['sum']).reset_index()
    return df
