import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import numpy as np
import time
from prophet.plot import plot_plotly, plot_components_plotly
from sklearn.metrics import r2_score
from datetime import datetime
import scipy
from time import perf_counter

# Importing the module
import os

start_time = time.perf_counter()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Getting the current working directory
cwd = os.getcwd()

# Printing the current working directory
# print("The Current working directory is: {0}".format(cwd))


df = pd.read_csv('test_input.csv')

print("Size of test_input.csv:", len(df))


if len(df) > 10000:
    df = df[0: 10000]
actual_time_buffer = df["ds"]
# Will fail if df longer than 10000 minutes



yraw = df["y"]

yfilt = []
for ind in range(0,len(yraw)):
    averaged = 0
    count = 0
    for j in range(max(0, ind - 7), min(ind + 7, len(yraw))):
        averaged += yraw[j]
        count += 1
    averaged = averaged / count
    yfilt.append(averaged)
#print(yfilt)
#for i in yfilt:
#    print(i)
# find peaks in smoothed signal
peaks, props = scipy.signal.find_peaks(yfilt, distance = 500, height = 25)
# find peaks in noisy signal using wavelet decomposition
cwt_peaks = scipy.signal.find_peaks_cwt(yraw, widths=np.arange(5, 15))

# print("peaks", peaks)
# print("cwt_peaks", cwt_peaks)

print("Number of Peaks:", peaks, "Peaks:", peaks)



# need to add functionality for when there is a gap in info
# maybe if gap in time then add datetime_ref in intervals
datetime_ref = pd.read_csv('datetime_day_ref.csv')

# will fail if df_time interval larger than gap
df_time_interval = df["ds"][len(df) - 1] - df["ds"][0] // (60 * 1000)
print(df_time_interval)

base = df["ds"][0]
for i in range(0, len(df)):
    #df["ds"][i] = pd.to_datetime(datetime_ref["ds"][(df["ds"][i] // (60 * 1000)) - base], unit='s')
    df["ds"][i] =  datetime.fromtimestamp(datetime_ref["ds"][(df["ds"][i] - base) // (60 * 1000)]).strftime("%Y-%m-%d")
    #df["ds"][i] = pd.to_datetime(df["ds"][i], format='%Y-%m-%d')
    
df['ds'] = pd.to_datetime(df['ds'])

# find diff in peaks
total_diff = 0
for i in range(1, len(peaks)):
    day_diff = (df["ds"][peaks[i]] - df["ds"][peaks[i - 1]]) / np.timedelta64(1, 'D')
    #print("day diff:", day_diff, df["ds"][peaks[i]], df["ds"][peaks[i - 1]])
    total_diff += day_diff
estimated_period = int(round(total_diff / (len(peaks) - 1)))

#print("ESTIMATED PERIOD:", estimated_period)

print("df head:", df.head())
print("df tail:", df.tail())

max_r2 = -1
max_period = -1
max_merged = -1
merged_dict = {}
max_forecast = -1

for p in range(estimated_period - 300, estimated_period + 700, 100):
    print(f"Testing period {p}")
    m = Prophet(weekly_seasonality = False, yearly_seasonality = False).add_seasonality(name='gassy', period=p, fourier_order = 10, prior_scale=0.1)
    m.fit(df)
    future = m.make_future_dataframe(periods=720)
    future.tail()
    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
    merged = forecast.merge(df, on="ds", how = 'outer')
    r2_merged = forecast.merge(df, on="ds", how = 'inner')
    r2 = r2_score(r2_merged["y"], r2_merged["yhat"])
    print("r2 score", r2, "max_r2", max_r2)
    if r2 > max_r2:
        max_r2 = r2
        max_period = p
        max_merged = merged
        max_forecast = forecast


# Python
#print("plotting forecast")
fig1 = m.plot(max_forecast)
#print(max_forecast.head())
#print(max_forecast.tail())

now_ind = len(actual_time_buffer)
now_date = max_merged["ds"][now_ind - 1]
for i in range(0, len(max_merged)):
    max_merged["ds"][i] = ((max_merged["ds"][i] - now_date) / np.timedelta64(1, 'D')) / 60

print("max_merged head:", max_merged.head())
print("max_merged tail:", max_merged.tail())
"""
# now ind shoule be len() since it is not considered in actual time buffer
now_ind = len(actual_time_buffer)
now_date = max_merged["ds"][now_ind]
for i in range(now_ind, len(max_merged)):
    max_merged["ds"][i] = (max_merged["ds"][i] - df["ds"][peaks[i - 1]]) / np.timedelta64(1, 'D')
"""

"""
max_merged["ds"] = actual_time_buffer
"""
max_merged.to_csv("yhat_current.csv", index=False)
"""
print(max_merged.head())
print(max_merged.tail())
"""

text_file = open("p_current.txt", "w")
n = text_file.write(str(max_period))
text_file.close()

#max_merged.set_index(max_merged["ds"])

plt.figure(figsize=(15,7))
plt.suptitle(f"ETH Gas Prices Over Time (period {max_period}, r2 = {round(max_r2, 2)})", fontsize=17)
plt.xlabel('Time / Hours')
plt.ylabel('Gas Price / Gwei')
plt.plot(max_merged["ds"], max_merged["y"], color='#D22A0D', label='Actual')
plt.plot(max_merged["ds"], max_merged["yhat"], color='#379BDB', label='Predicted')

plt.legend(loc='best')
plt.savefig('yhat_graph_current.png')

end_time = time.perf_counter()

print("YHAT GENERATION TIME TAKEN:", (end_time - start_time) / 60)
#plt.show()