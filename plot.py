import pandas as pd
import numpy as np
import sys
import os
from termcolor import colored

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
with open(obsFileName,mode='r') as f:
    for x in range(100):
        head = next(f)
        obsColumns.append(head.strip())
        if head.strip() == '######':
            print(x-1)
            break

obsColumns = obsColumns[1:len(obsColumns)-1]
obsColumns
print(obsColumns)





