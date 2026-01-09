import pandas as pd 
print(pd.__version__)

from prophet import Prophet 
import numpy as np
np.float = float
np.int = int

import holidays
us_holidays = holidays.US()

data = input_table_1.copy()

itemlist = input_table_1['SalesItem'].unique()
m = Prophet(holidays=None)
fcst_all = pd.DataFrame() 

for x in itemlist:
    temp = data[data.SalesItem == x]
    temp = temp.drop(columns=[ 'SalesItem','Plant'])
    temp['SalesDate'] = pd.to_datetime(temp['SalesDate'])
    temp = temp.set_index('SalesDate')

    d_df = temp.resample('MS').sum()
    d_df = d_df.reset_index().dropna()
    d_df.columns = ['ds', 'y']
    try:
        m = Prophet(weekly_seasonality=True, daily_seasonality=True, seasonality_mode='additive', interval_width=0.95, holidays=None).fit(d_df)
        future = m.make_future_dataframe(periods=6, freq='MS')
        
    except ValueError:
        pass       

    fcst = m.predict(future)
    fcst['SalesItem'] = x  
    fcst['Fact'] = d_df['y'].reset_index(drop=True)
    fcst_all = pd.concat([fcst_all, fcst], axis=0, ignore_index=True)
    print(x)
    
fcst_all.set_index(['ds', 'yhat', 'SalesItem'], inplace=True, append=True, drop=False)
output_table_1 = fcst_all.copy()