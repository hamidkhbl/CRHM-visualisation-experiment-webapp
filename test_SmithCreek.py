#%%
import pandas as pd 
import numpy as np 

#%%
# Convert obs to csv
def convertToCsv(fileName):
    df = pd.read_csv(fileName, sep = '\t')
    df.to_csv('csv/{0}.csv'.format(fileName))
    #print('converted {0} to csv'.format(fileName))

convertToCsv('CRHM_output_SmithCreek_gcc.obs')
convertToCsv('CRHM_output_SmithCreek_vcc.obs')

#%%

df_gcc = pd.read_csv('csv/CRHM_output_SmithCreek_gcc.obs.csv', index_col=False)
df_vcc = pd.read_csv('csv/CRHM_output_SmithCreek_vcc.obs.csv', index_col=False)

df = df_gcc.merge(df_vcc, right_on = df_gcc.index, left_on = df_vcc.index)
# WS_outflow@F(1),WS_outflow@F(2),WS_outflow@F(3),WS_outflow@F(4),WS_outflow@F(5)

df['WS1_diff'] = abs(df_gcc['WS_outflow@F(1)'] - df_vcc['WS_outflow@F(1)'])
df['WS2_diff'] = abs(df_gcc['WS_outflow@F(2)'] - df_vcc['WS_outflow@F(2)'])
df['WS3_diff'] = abs(df_gcc['WS_outflow@F(3)'] - df_vcc['WS_outflow@F(3)'])
df['WS4_diff'] = abs(df_gcc['WS_outflow@F(4)'] - df_vcc['WS_outflow@F(4)'])
df['WS5_diff'] = abs(df_gcc['WS_outflow@F(5)'] - df_vcc['WS_outflow@F(5)'])

df.to_csv('SmithCreek_full_diff.csv')

