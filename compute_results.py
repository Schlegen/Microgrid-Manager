import os
current_path = os.path.abspath('')

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

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

if __name__ == "__main__":

    x = [0.0 for i in range(5 * 48)]

    x_forecast_memory = np.zeros(((DAY_END - DAY_BEGIN) // ONE_STEP, 14 * 48))
    net_demand_forecast_memory = np.zeros(((DAY_END - DAY_BEGIN) // ONE_STEP, 14 * 48))
    last_x_memory = np.zeros(((DAY_END - DAY_BEGIN) // ONE_STEP, 5 * 48))
    last_net_demand_memory = np.zeros(((DAY_END - DAY_BEGIN) // ONE_STEP, 5 * 48))

    for i in range((DAY_END - DAY_BEGIN) // ONE_STEP):
        print(i)

        day = DAY_BEGIN + i * ONE_STEP
        two_last_weeks = lt_1213.customers[0].net_load[(day-DATA_BEGIN) // ONE_STEP - 14*48 : (day-DATA_BEGIN) // ONE_STEP]

        two_next_weeks = forecast_two_next_weeks(two_last_weeks, res, 14*48)
        p_buy, p_sell = forecast_prices(day, P_PURCHASE, P_SALE, step=ONE_STEP)

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

        #advised_battery_load = [dict_var['battery_load_' + str(i)] for i in range(len(two_next_weeks)-1)]

        x_forecast = [dict_var['battery_state_' + str(i)] for i in range(len(two_next_weeks)-1)]

        x.append(x_forecast[1])

        x_forecast_memory[i,:] = x_forecast
        net_demand_forecast_memory[i,:] = two_next_weeks
        last_x_memory[i,:] = x
        last_net_demand_memory[i,:] = lt_1213.customers[0].net_load[(day - DATA_BEGIN) // ONE_STEP - 5*48 : (day-DATA_BEGIN) // ONE_STEP]

        # time_series_to_json(
        #     time_series=two_last_weeks + two_next_weeks,
        #     series_begin=day - 48 * 14 * ONE_STEP,
        #     one_step=ONE_STEP,
        #     file_name='static/net_demand.json'
        #     )
        #
        # time_series_to_json(
        #     time_series=x[(day-DATA_BEGIN) // ONE_STEP - 14*48 : (day-DATA_BEGIN) // ONE_STEP] + x_forecast[1:],
        #     series_begin=day - 48 * 14 * ONE_STEP,
        #     one_step=ONE_STEP,
        #     file_name='static/x.json'
        #     )

    np.save("save/x_forecast_memory", x_forecast_memory)
    np.save("save/net_demand_forecast_memory", net_demand_forecast_memory)
    np.save("save/last_x_memory", last_x_memory)
    np.save("save/last_net_demand_memory", last_net_demand_memory)

    #print(x_forecast_memory)
    #print(net_demand_forecast_memory)
    #print(last_x_memory)
    #print(last_net_demand_memory)
