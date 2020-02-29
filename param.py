import os
current_path = os.path.abspath('')

import numpy as np
from tools import (
    Customer,
    DataFrame,
    load_data_frame
)
from datetime import date, datetime, timedelta

# loading the data
lt_1213 = load_data_frame("save/customers1213.txt")
data_train = lt_1213.customers[0].net_load[0:14*48]

# parameters
RHO_C = 0.95
RHO_D = 0.95
U_LOW = -1
U_UP = 1
X_LOW = 0
X_UP = 5

prices = np.loadtxt(os.path.join(current_path, "save/prices.csv"))
P_PURCHASE = prices[1, :]
P_SALE = prices[2, :]

# beginning of the data
DATA_BEGIN = datetime(year=2012, month=7, day=1, hour=0, minute=0)

# beginning of the simulation
DAY_BEGIN = datetime(year=2012, month=7, day=15, hour=0, minute=0)
DAY_END = datetime(year=2012, month=7, day=30, hour=0, minute=0)
ONE_STEP = timedelta(minutes=30)

# Deciding whether we refit the forecasting model

REFIT_MODEL = False
