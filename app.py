# -*- coding: utf-8 -*-
import webbrowser
from threading import Timer
from flask import Flask, render_template, jsonify
import json
import requests
import random as rd
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta, timezone
from time import time
from tools import Customer, DataFrame, time_series_to_json
from param import (
    RHO_C,
    RHO_D,
    U_LOW,
    U_UP,
    X_LOW,
    X_UP,
    lt_1213,
    P_PURCHASE,
    P_SALE,
    DAY_BEGIN,
    DAY_END,
    DATA_BEGIN,
    ONE_STEP
)
from forecast import res, forecast_two_next_weeks, forecast_prices
from optimisation import solve_optim

app = Flask(__name__)
#i = 0
#last_dico = None

@app.route("/")
def hello():
    return render_template('dashboard.html')


@app.route('/data')
def get_data():
    global i
    global last_execution
    global last_dico
    global x

    if i == -1 or time() - last_execution > 7:
        print(i)
        i += 1
        last_execution = time()

        day = DAY_BEGIN + i * ONE_STEP
        two_last_weeks = lt_1213.customers[0].net_load[(day-DATA_BEGIN) // ONE_STEP - 14*48 : (day-DATA_BEGIN) // ONE_STEP]

        two_next_weeks = forecast_two_next_weeks(two_last_weeks, res, 14*48)

#lt_1213.customers[0].net_load[(day-DATA_BEGIN) // ONE_STEP : (day-DATA_BEGIN) // ONE_STEP + 14*48 ]
#forecast_two_next_weeks(two_last_weeks, res, 14*48)

        p_buy, p_sell = forecast_prices(day, P_PURCHASE, P_SALE, step=ONE_STEP)

        charging = x[-1] - x[-2]

        loss = 0
        if charging > 0:
            loss = (1/0.95 - 1) * charging;
        else:
            loss = 0.05 * charging

        imported = charging + two_last_weeks[-1] + loss

        dict_var = solve_optim(
            forecast=two_next_weeks,
            rho_c=RHO_C,
            rho_d=RHO_D,
            u_low=U_LOW,
            u_up=U_UP,
            x_low=X_LOW,
            x_up=X_UP,
            last_x=x[-1],
            p_buy=p_buy,
            p_sell=p_sell,
            index=i
            )

        x_forecast = np.array([dict_var['battery_state_' + str(k)] for k in range(len(two_next_weeks)-1)])

        net_demand = np.concatenate((two_last_weeks, two_next_weeks))
        battery = np.concatenate((x[-14*48:], x_forecast[1:]))
        series_begin = day - 48 * 14 * ONE_STEP

        x.append(x_forecast[1])


        # in the dictionary, we give the prediction as well as the relevant values for the last 30 minutes( in order to update the scheme)
        dico = {
            "time" : i,
            "net_demand" : [[(series_begin + i * ONE_STEP).replace(tzinfo=timezone.utc).timestamp()*1000, net_demand[i]] for i in range(len(net_demand))],
            "battery" : [[(series_begin + i * ONE_STEP).replace(tzinfo=timezone.utc).timestamp()*1000, battery[i]] for i in range(len(battery))],
            "generation" : lt_1213.customers[0].GG[(day-DATA_BEGIN) // ONE_STEP - 1],
            "demand" : lt_1213.customers[0].GC[(day-DATA_BEGIN) // ONE_STEP - 1],
            "imported" : imported
            }

        last_execution = time()
        last_dico = jsonify(dico)

        return jsonify(dico)

    else:
        print(i, "else", time())

        return(last_dico)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == "__main__":
    last_execution = time()
    last_dico = None
#    last_delivery = 0
    i = -1
    x = [0.0 for j in range((DAY_BEGIN - DATA_BEGIN) // ONE_STEP )]
    Timer(1, open_browser).start();
    app.run(debug=True)
