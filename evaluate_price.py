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
    """
    p_sell is a tab containing the selling prices
    p_buy is a tab containing the buying prices
    net_load is the net load of the microgrid

    this function evaluates the cost of the electricity on the microgrid
    if we had not the battery. In this case, we export the net_load when
    it is negative andwe import when it is positive.
    """
    cost = [0]
    for i in range(len(net_demand)):

        if net_demand[i] >= 0:
            cost.append(cost[-1] + p_buy[i] * net_demand[i])

        else:
            cost.append(cost[-1] + p_sell[i] * net_demand[i])

    return(cost)

def evaluate_clairvoyant(p_sell, p_buy, net_demand):
    """
    p_sell is a tab containing the selling prices
    p_buy is a tab containing the buying prices
    net_load is the net load of the microgrid

    this function evaluates the cost of the electricity on the microgrid
    if the solution were optimal
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
