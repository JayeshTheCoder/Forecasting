import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from numpy.linalg import LinAlgError
from scipy import linalg

pd.options.display.max_columns = 99
plt.rcParams['figure.figsize'] = (12, 8)

df_train = input_table_1.copy()
df_test = input_table_2.copy()

df_train = df_train.set_index('date')
df_test = df_test.set_index('date')

sarima_results = df_test.reset_index()
sarima_results['sales'] = 0


tic = time.time()

for s in sarima_results['store'].unique():
    for i in sarima_results['item'].unique():
        si = df_train.loc[(df_train['store'] == s) & (df_train['item'] == i), 'sales']
        
        #si.index = pd.DatetimeIndex(si.index).to_period('M')
        #si = np.asarray(si)
        
        sarima = sm.tsa.statespace.SARIMAX(si.astype(float), trend='n', freq='MS', enforce_invertibility=False,
                                           order=(1, 1, 1),seasonal_order=(1, 1, 1, 6),initialization='approximate_diffuse')
        results = sarima.fit()
        print(linalg.lapack.dgetrf([np.nan]))
        print(linalg.lapack.dgetrf([np.inf]))
        
        fcst = results.predict(start='2022-04-01', end='2022-09-01', dynamic=True)
        sarima_results.loc[(sarima_results['store'] == s) & (sarima_results['item'] == i), 'sales'] = fcst.values[0:]
        
        toc = time.time()
        if i % 10 == 0:
            print("Completed store {} item {}. Cumulative time: {:.1f}s".format(s, i, toc-tic))
            
sarima_results.to_csv('sarima_results_in12_Feb_114_KNIME.csv', index=False)

output_table_1 = sarima_results.copy()