import time
import threading
from collections import deque
from gas_getter import *
from datetime import datetime, timezone
from csv import writer
import pandas as pd

# Importing the module
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Getting the current working directory
cwd = os.getcwd()

# Printing the current working directory
# print("The Current working directory is: {0}".format(cwd))

def csv_appender(csv_name, row):
    df = pd.read_csv(csv_name)

    print("inserting row:", row)
    df_extended = pd.DataFrame([row], columns=['ds', 'y'])
    # print("df_extended", df_extended)
    if len(df) >= 3600:
        df = df[1:]
    df2 = pd.concat([df, df_extended])
    df2.to_csv(csv_name, index=False )

def update_queue():
    gas_info = gas_getter()
    # print(gas_info)
    safe_gas_price = gas_info["result"]["SafeGasPrice"]
    utc_time = datetime.now(timezone.utc).timestamp() * 1000
    print("gas price:", safe_gas_price)
    csv_appender("./test_input.csv", [str(round(float(utc_time))), str(round(float(safe_gas_price)))])

update_queue()



