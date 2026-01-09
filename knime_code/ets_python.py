import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt


data = input_table_1.copy()

data1 = data[['SalesDate','Consumption']]
data1 = data1.set_index("SalesDate")

from statsmodels.tsa.api import SimpleExpSmoothing

#First Instance
ins2 = Holt(data1.astype(float)).fit(smoothing_level=0.2,optimized=False, smoothing_slope=.08)
ins_cast2 = ins2.forecast(6).rename('alpha=0.8')
forecast = pd.DataFrame(ins_cast2)

df = pd.concat([data1,forecast])


output_table_1 = df.copy()