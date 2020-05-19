import numpy as np 
import pandas as pd
import plotly.offline as pyo 
import plotly.graph_objects as go 

df = pd.read_csv('csv/crhm.obs.csv', index_col= False)

trace0 = go.Scatter(x=df['time'], 
                    y=df['SWE(1)'], 
                    mode='lines', 
                    name='SWE(1)')

trace1 = go.Scatter(x=df['time'], 
                    y=df['SWE(2)'], 
                    mode='lines', 
                    name='SWE(1)')


trace2 = go.Scatter(x=df['time'], 
                    y=df['SWE(3)'], 
                    mode='lines', 
                    name='SWE(1)')

data = [trace0, trace1, trace2]

layout = go.Layout(title='Bad Lake')

fig = go.Figure(data=data, layout=layout)

pyo.plot(fig)