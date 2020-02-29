import os
current_path = os.path.abspath('')
import json
import numpy as np
from tools import (
    Customer,
    DataFrame,
    load_data_frame
)
from datetime import date, datetime, timedelta, timezone
from param import lt_1213, DATA_BEGIN, ONE_STEP

data = lt_1213.customers[0].net_load

def time_series_to_json(time_series, data_begin, one_step, data):
    rep = [[(data_begin + i * one_step).replace(tzinfo=timezone.utc).timestamp()*1000, time_series[i]] for i in range(len(time_series))]
    with open('save/data.json', 'w') as json_file:
        json.dump(rep, json_file)

time_series_to_json(data, DATA_BEGIN, ONE_STEP)
