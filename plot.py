import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.style.use('seaborn-pastel')

import os
current_path = os.path.abspath('')
path_to_data = path_to_data = os.path.join(current_path, "data.csv")
import pandas as pd
import numpy as np
plt.style.use('fivethirtyeight')
import random as rd
from datetime import date, datetime, timedelta
import matplotlib.dates as mdates
from tools import Customer, DataFrame
from param import (
#    lt_1213,
    P_PURCHASE,
    P_SALE,
    DAY_BEGIN,
    DAY_END,
    DATA_BEGIN,
    ONE_STEP
)
from forecast import forecast_prices

def plot_battery(x_forecast_memory, net_demand_forecast_memory, last_x_memory, last_net_demand_memory):

    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 5))
    line_forecast1, = ax1.plot([], [], color="DarkOrange")
    line_past1, = ax1.plot([],[], color="Blue")
    lines1 = [line_forecast1, line_past1]

    ax1.set_xlim(0,14 * 48)
    ax1.set_ylim(-0.1, 6)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Génération Electrique (kWh)')
    ax1.set_title("Chargement de la batterie")
    plt.legend(bbox_to_anchor=(0.8, 0.8))

    fig2, ax2 = plt.subplots(1, 1, figsize=(18, 5))
    line_forecast2, = ax2.plot([], [], color="DarkOrange")
    line_past2, = ax2.plot([],[], color="Blue")
    lines2 = [line_forecast2, line_past2]

    ax2.set_xlim(0,14 * 48)
    ax2.set_ylim(-3, 3)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Génération Electrique (kWh)')
    ax2.set_title("Prédiction de la demande nette")
    #plt.legend(bbox_to_anchor=(0.8, 0.8))

    def animate1(i):
        print(i, " begin")

        instant = DAY_BEGIN + i * ONE_STEP
        x_forecast = x_forecast_memory[i,:]
        previous_x = last_x_memory[i,:]

        ax1.set_xlim(instant - 5 * 48 * ONE_STEP, instant + 14 * 48 * ONE_STEP)
        lines1[0].set_data([instant + i * ONE_STEP for i in range(len(x_forecast))], x_forecast)
        lines1[1].set_data([instant + (i - 5 * 48) * ONE_STEP for i in range(len(previous_x))], previous_x)
        return lines1


    def animate2(i):
        print(i, " begin")

        instant = DAY_BEGIN + i * ONE_STEP
        net_demand_forecast = net_demand_forecast_memory[i,:]
        previous_net_demand = last_net_demand_memory[i,:]

        ax2.set_xlim(instant - 5 * 48 * ONE_STEP, instant + 14 * 48 * ONE_STEP)
        lines2[0].set_data([instant + i * ONE_STEP for i in range(len(net_demand_forecast))], net_demand_forecast)
        lines2[1].set_data([instant + (i - 5 * 48) * ONE_STEP for i in range(len(previous_net_demand))], previous_net_demand)
        return lines2

    ani = [
        animation.FuncAnimation(fig=fig1, func=animate1, frames=(DAY_END - DAY_BEGIN) // ONE_STEP, interval=100, blit=True),
        animation.FuncAnimation(fig=fig2, func=animate2, frames=(DAY_END - DAY_BEGIN) // ONE_STEP, interval=100, blit=True)
        ]

    plt.show()

if __name__ == "__main__":

    x_forecast_memory = np.load("save/x_forecast_memory.npy")
    net_demand_forecast_memory = np.load("save/net_demand_forecast_memory.npy")
    last_x_memory = np.load("save/last_x_memory.npy")
    last_net_demand_memory = np.load("save/last_net_demand_memory.npy")

    plot_battery(x_forecast_memory, net_demand_forecast_memory, last_x_memory, last_net_demand_memory)
