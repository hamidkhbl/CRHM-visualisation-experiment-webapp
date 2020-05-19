import pandas as pd
import numpy as np
import sys
import os
from termcolor import colored
import plotly.offline as pyo 
import plotly.graph_objects as go 
from plot import converttoDF, checkTime, plot
import random
import secrets

obsFile1 = sys.argv[1]
obsFile2 = sys.argv[2]
mode = sys.argv[3]    

if mode == 'time':
    df1 = checkTime(converttoDF(obsFile1))
    df2 = checkTime(converttoDF(obsFile2))
    df = df1.merge(df2, left_on = 'time', right_on = 'time')
    df.to_csv('merged.csv')

elif mode == 'id':
    df1 = checkTime(converttoDF(obsFile1))
    df2 = checkTime(converttoDF(obsFile2))
    df = df1.merge(df2, left_on = df1.index, right_on = df2.index)
    del df['time_y'], df['key_0']
    df = df.rename(columns={'time_x':'time'})

else:
    print(colored('Error','red'), ': mode should be id or time.')

plot(df,'{0} and {1} comparison'.format(obsFile1,obsFile2))