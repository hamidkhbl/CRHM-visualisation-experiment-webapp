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

# read the obs file
with open(obsFileName,mode='r') as f:
    content = f.read()
print(content.index("SWE(1)"))



