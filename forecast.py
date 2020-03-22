import pandas as pd
import numpy as np
from copy import copy
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults
from tools import (
    Customer,
    DataFrame,
    load_data_frame,
)
from datetime import date, datetime, timedelta
from param import lt_1213, data_train, REFIT_MODEL, SAVE_MODEL

## ------------------- Prédiction de la demande nette -------------------------

# -------------------- Choice of the Parameters -------------------------------

if REFIT_MODEL:

    p = 2
    d = 0
    q = 2

    s = 48

    P = 1
    D = 1
    Q = 0

# ------------------- fitting of the model ------------------------------------

    mod = SARIMAX(
        endog=data_train ,
        exog=None,
        order=(p, d, q),
        seasonal_order=(P, D, Q, s),
        trend=None,
        measurement_error=False,
        time_varying_regression=False,
        mle_regression=True,
        simple_differencing=False,
        enforce_stationarity=False,
        enforce_invertibility=False,
        hamilton_representation=False,
        concentrate_scale=False,
        trend_offset=1,
        use_exact_diffuse=False,
        dates=None,
        freq=None,
        missing='none'
    )

    res = mod.fit(disp=False)

    if SAVE_MODEL:
        res.save('save/prediction_model.pkl')

else:

    res = SARIMAXResults.load('save/prediction_model.pkl')

# ------------------------------ Prediction -----------------------------------

def forecast_two_next_weeks(two_last_weeks, res, length):
    """Predicts the two next weeks of a time series from the last two weeks using
     the SARIMAX method above

    Arguments:
        two_last_weeks {float tab} -- Two last weeks of the time series from which we predict
        res {statsmodels.tsa.statespace.sarimax.SARIMAXResults} -- prediction model (defined above)
        length {int} -- length of the prediction

    Returns:
        float np.array -- forecast of the next values of the time series

    """
    res_test = res.apply(two_last_weeks, refit=False)

    return res_test.forecast(length)

def forecast_prices(time, p_purchase, p_sale, step, n_days):
    """Predicts the prices for the n_days following the date time

    Arguments:
        time {datetime} -- time from which we predict the prices
        p_purchase {float tab} -- tab containing the
        p_sale {float tab} -- [description]
        step {datetime.timedelta} -- [description]
        n_days {int} -- number

    Returns:
        float np.array -- prices of import for the coming n_days
        float np.array -- prices of export for the coming n_days
    """

    day_begin = datetime(
        year=time.year,
        month=time.month,
        day=time.day,
        hour=0,
        minute=0
    )

    time_begin = (time - day_begin) // step

    p_buy = np.concatenate((
        np.concatenate(
            (p_purchase[time_begin:],
            np.tile(p_purchase, n_days - 1)),
            axis=0
            ),
        p_purchase[:time_begin]),
        axis=0
    )

    p_sell = np.concatenate((
        np.concatenate(
            (p_sale[time_begin:],
            np.tile(p_sale, n_days - 1)),
            axis=0
            ),
        p_sale[:time_begin]),
        axis=0
    )

    return p_buy, p_sell
