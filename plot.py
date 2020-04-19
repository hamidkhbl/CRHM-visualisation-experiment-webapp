import pandas as pd
import numpy as np
import sys
import os
from termcolor import colored
import plotly.offline as pyo 
import plotly.graph_objects as go 

obsFileName = sys.argv[1]

# create csv folder
if not os.path.exists('csv'):
    os.makedirs('csv')

# covert obs to csv
def convertToCsv(fileName):
    print(colored("Info",'green'),": converting obs to csv...")
    df = pd.read_csv(fileName, sep = '\t')
    df.to_csv('csv/{0}.csv'.format(fileName))
    print(colored("Info",'green'),": csv format of {0} saved to csv folder.".format(fileName))

# read header of the obs file
obsColumns = []
headerCount = 0
with open(obsFileName,mode='r') as f:
    for x in range(100):
        head = next(f)
        obsColumns.append(head.strip())
        if head.strip() == '######':
            headerCount = x +1
            break
obsColumns = obsColumns[1:len(obsColumns)-1]

# read body of the obs file
with open(obsFileName,mode='r') as f:
    body = f.read()
body = body.split("\n",headerCount)[headerCount]
bodyList = body.split('\n')
# convert body to dataframe

obsColumnsTm = ['time'] + obsColumns

df = pd.DataFrame([x.split('\t') for x in bodyList], columns = obsColumnsTm)

df.to_csv('test.csv')

data = []
for x in obsColumns:
    trace = go.Scatter(x=df['time'], 
                        y=df[x], 
                        mode='lines',
                        name=x)
    data.append(trace)
print(colored('Info','green')," Generating plot for {}...".format(obsFileName))
layout = go.Layout(title=obsFileName)
fig = go.Figure(data=data, layout=layout)
pyo.plot(fig)





