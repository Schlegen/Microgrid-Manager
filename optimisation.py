import os
from random import randint

import numpy as np
from forecast import res, forecast_two_next_weeks, forecast_prices

import pulp

def solve_optim(forecast, rho_c, rho_d, u_low, u_up, x_low, x_up, last_x, p_buy, p_sell, index):
    """Given a forecast, and parameters of the problem, compute the battery management that minimizes the cost for the period of the forecast

    Arguments:
        forecast {float np.array} -- net demand forecast
        rho_c {float} -- parameters that modelize the Joule effect when the battery charges
        rho_d {float} -- parameters that modelize the Joule effect when the battery discharges
        u_low {float} -- minimal energy influx in the battery cable for 30 minutes
        u_up {float} -- maximal energy influx in the battery cable for 30 minutes
        x_low {float} -- minimum charge of the battery
        x_up {float} -- maximum charge of the battery (= capacity)
        last_x {float} -- charge of the battery when we solve the problem
        p_buy {float np.array} -- import prices for the duration of the forecast
        p_sell {float np.array} -- export prices for the duration of the forecast
        index {int} -- Index that identifies

    Returns:
        dictionary -- contains the values all the solution variables
    """

    # Model

    model = pulp.LpProblem(f"Min_Cost_problem_{index}", pulp.LpMinimize)

    # Variables

    u = pulp.LpVariable.dicts(
        name = 'battery_load',
        indexs = range(len(forecast)-1),
        lowBound = u_low,
        upBound = u_up,
        cat = pulp.LpContinuous
    )

    x = pulp.LpVariable.dicts(
        name = 'battery_state',
        indexs = range(len(forecast)),
        lowBound = x_low,
        upBound = x_up,
        cat = pulp.LpContinuous
    )

    # parties positves et négatives

    u_plus = pulp.LpVariable.dicts(
        name = 'battery_load_positive_part',
        indexs = range(len(forecast)-1),
        lowBound = 0,
        cat = pulp.LpContinuous
    )

    u_minus = pulp.LpVariable.dicts(
        name = 'battery_load_negative_part',
        indexs = range(len(forecast)-1),
        lowBound = 0,
        cat = pulp.LpContinuous
    )

    l_plus = pulp.LpVariable.dicts(
        name = 'delivery_positive_part',
        indexs = range(len(forecast)-1),
        lowBound = 0,
        cat = pulp.LpContinuous
    )

    l_minus = pulp.LpVariable.dicts(
        name = 'delivery_negative_part',
        indexs = range(len(forecast)-1),
        lowBound = 0,
        cat = pulp.LpContinuous
    )

    # Objective function

    objective = pulp.lpSum([(p_buy[i] * l_plus[i]) - (p_sell[i] * l_minus[i]) for i in range(len(forecast)-1)])
    model += objective, "Cost"

    # Constraints

    label0 = f"Battery_state_continuity"
    constraint0 = x[0] == last_x
    model += constraint0, label0

    for i in range(len(forecast)-1):

        label1 = f"Joule_effect_{i}"
        constraint1 = (
            x[i+1] == x[i] + rho_c * u_plus[i] - (1 / rho_d) * u_minus[i]
            )
        model += constraint1, label1

        label2 = f"Positive_part_of_l[{i}]"
        constraint2 = l_plus[i] >= forecast[i+1] + u[i]
        model += constraint2, label2

        label3 = f"Negative_part_of_l[{i}]"
        constraint3 = l_plus[i] - l_minus[i] == forecast[i+1] + u[i]
        model += constraint3, label3

        label4 = f"Positive_part_of_u[{i}]"
        constraint4 = u_plus[i] >= u[i]
        model += constraint4, label4

        label5 = f"Negative_part_of_u[{i}]"
        constraint5 = u_plus[i] - u_minus[i] == u[i]
        model += constraint5, label5

    #pulp.LpSolverDefault.msg = 1
    model.solve()

    varsdict = {}
    for v in model.variables():
        varsdict[v.name] = v.varValue

    #print(pulp.value(model.objective))

    return varsdict
