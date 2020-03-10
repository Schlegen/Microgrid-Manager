from optimisation import solve_optim
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

def evaluate_without_battery(p_sell, p_buy, net_demand):
    """ Evaluates the cost of the electricity on the microgrid
    if we had not the battery. In this case, we export the net_load when
    it is negative andwe import when it is positive.

    Arguments:
        p_sell {tab of floats} -- selling prices for the period
        p_buy {tab of floats} -- buying prices for the period
        net_demand {tab of floats} -- net load of the microgrid for the period

     Returns:
        tab of float -- tab containing the cumulative cost of the case without battery
    """
    cost = [0]
    for i in range(1, len(net_demand)):

        if net_demand[i] >= 0:
            cost.append(cost[-1] + p_buy[i] * net_demand[i])

        else:
            cost.append(cost[-1] + p_sell[i] * net_demand[i])

    return cost

def evaluate_clairvoyant(p_sell, p_buy, net_demand):
    """this function evaluates the cost of the electricity on the microgrid
    if the prediction were optimal

    Arguments:
        p_sell {tab of floats} -- selling prices for the period
        p_buy {tab of floats} -- buying prices for the period
        net_demand {tab of floats} -- net load of the microgrid for the period

    Returns:
        tab of float -- tab containing the cumulative cost of the clairvoyant case
    """
    cost = [0]

    dict_var = solve_optim(
        forecast=net_demand,
        rho_c=RHO_C,
        rho_d=RHO_D,
        u_low=U_LOW,
        u_up=U_UP,
        x_low=X_LOW,
        x_up=X_UP,
        last_x=0,
        p_buy=p_buy,
        p_sell=p_sell,
        index=0
        )

    for i in range(len(net_demand) - 1):
        cost.append(
            cost[-1] + dict_var['delivery_positive_part_' + str(i)] * p_buy[i] - dict_var['delivery_negative_part_' + str(i)] * p_sell[i]
        )
    return cost

def evaluate(p_sell, p_buy, u, net_demand):
    cost = [0]

    for i in range(len(u)):
        imported = u[i] + net_demand[i+1]

        if imported > 0:
            cost.append(cost[-1] + imported * p_buy[i])
        else:
            cost.append(cost[-1] + imported * p_sell[i])

    return cost
