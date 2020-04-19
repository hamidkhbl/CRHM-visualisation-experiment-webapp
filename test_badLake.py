#%%
import pandas as pd 
import numpy as np 

#%%
# Convert obs to csv
def convertToCsv(fileName):
    df = pd.read_csv(fileName, sep = '\t')
    df.to_csv('csv/{0}.csv'.format(fileName))
    #print('converted {0} to csv'.format(fileName))

convertToCsv('CRHM_output_1.obs')
convertToCsv('crhm.obs')
convertToCsv('CRHM_output_1_vcc.obs')
#%%
#Calculate diff
df_gcc = pd.read_csv('csv/CRHM_output_1.obs.csv', index_col=False)
df_crhm = pd.read_csv('csv/crhm.obs.csv',index_col=False)
df_vcc = pd.read_csv('csv/CRHM_output_1_vcc.obs.csv',index_col=False)

df_tmp = df_gcc.merge(df_crhm, left_on=df_gcc.index, right_on=df_crhm.index)
df_tmp = df_tmp.rename (columns ={'key_0':'key_1'})
#%%
df = df_tmp.merge(df_vcc, left_on=df_tmp.index, right_on=df_vcc.index)
df.to_csv('csv/full_diff.csv')

df['SWE(1)_diff_gcc_crhm'] = abs(df['SWE(1)_x'] - df['SWE(1)_y'])
df['SWE(2)_diff_gcc_crhm'] = abs(df['SWE(2)_x'] - df['SWE(2)_y'])
df['SWE(3)_diff_gcc_crhm'] = abs(df['SWE(3)_x'] - df['SWE(3)_y'])

df['SWE(1)_diff_gcc_vcc'] = abs(df['SWE(1)_y'] - df['SWE(1)'])
df['SWE(2)_diff_gcc_vcc'] = abs(df['SWE(2)_y'] - df['SWE(2)'])
df['SWE(3)_diff_gcc_vcc'] = abs(df['SWE(3)_y'] - df['SWE(3)'])

df['SWE(1)_diff_vcc_crhm'] = abs(df['SWE(1)_x'] - df['SWE(1)'])
df['SWE(2)_diff_vcc_crhm'] = abs(df['SWE(2)_x'] - df['SWE(2)'])
df['SWE(3)_diff_vcc_crhm'] = abs(df['SWE(3)_x'] - df['SWE(3)'])



treshold = 0

df_diff = df[['time_x','time_y','SWE(1)_diff_gcc_crhm','SWE(2)_diff_gcc_crhm','SWE(3)_diff_gcc_crhm']]


print('Number of missmatches: {}'.format(len (df_diff[ (df_diff['SWE(1)_diff_gcc_crhm'] > treshold) |
                                                       (df_diff['SWE(2)_diff_gcc_crhm'] > treshold) |
                                                       (df_diff['SWE(3)_diff_gcc_crhm'] > treshold)
                                                       ])))
df_diff.to_csv('csv/diff.csv')
# %%
