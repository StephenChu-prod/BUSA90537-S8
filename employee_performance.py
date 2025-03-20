#Determining the most productive employee
'''
Most productive employee is determined by 3 metrics (from most priority to least):
(1) Performance Review result (5: most productive, 1: least productive)
(2) Median of work hours (lower median : higher productivity)
(3) Count of workday (higher count of workday : higher productivity)
'''
productive_emp_base = data.groupby(['Employee Number','Performance Review'])['Hours Worked'].agg(['median','count']).reset_index()
productive_emp_base.sort_values(by = ['Performance Review','median','count'], ascending = [False,True,False]).reset_index(drop=True)

#Total hours worked for the whole period
total_hrs_emp_base = data.groupby('Employee Number')['Hours Worked'].agg(['sum']).reset_index()