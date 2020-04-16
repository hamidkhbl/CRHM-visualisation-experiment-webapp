#,time,
# WS_outflow@F(1),
# WS_outflow@F(2),
# WS_outflow@F(3),
# WS_outflow@F(4),
# WS_outflow@F(5)
import numpy as np 
import pandas as pd
import plotly.offline as pyo 
import plotly.graph_objects as go 

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

df = pd.read_csv('csv/CRHM_output_SmithCreek_gcc.obs.csv', index_col= False)
df['time'] = df['time'].apply(lambda x : rreplace(x, ' ',':',1))
df['time'] = df['time'].apply(lambda x : rreplace(x, ' ','-',4))
df['time'] = df['time'].apply(lambda x : rreplace(x, '-',' ',1))

print(df.head())

trace0 = go.Scatter(x=df['time'], 
                    y=df['WS_outflow@F(1)'], 
                    mode='lines', 
                    name='WS_outflow@F(1)')

trace1 = go.Scatter(x=df['time'], 
                    y=df['WS_outflow@F(2)'], 
                    mode='lines', 
                    name='WS_outflow@F(2)')


trace2 = go.Scatter(x=df['time'], 
                    y=df['WS_outflow@F(3)'], 
                    mode='lines', 
                    name='WS_outflow@F(3)')

trace3 = go.Scatter(x=df['time'], 
                    y=df['WS_outflow@F(4)'], 
                    mode='lines', 
                    name='WS_outflow@F(4)')

trace4 = go.Scatter(x=df['time'], 
                    y=df['WS_outflow@F(5)'], 
                    mode='lines', 
                    name='WS_outflow@F(5)')


data = [trace0, trace1, trace2, trace3, trace4]

layout = go.Layout(title='Smith Creek')

fig = go.Figure(data=data, layout=layout)

pyo.plot(fig)