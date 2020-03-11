import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
    lt_1213,
    P_PURCHASE,
    P_SALE,
    DAY_BEGIN,
    DAY_END,
    DATA_BEGIN,
    ONE_STEP
)
from forecast import forecast_prices
from matplotlib import rc
from statsmodels.graphics.tsaplots import plot_acf
from evaluate_cost import evaluate_without_battery, evaluate_clairvoyant, evaluate

def plot_demand(day_begin_plot):
    """Plots 3 days of demand
    
    Arguments:
        day_begin_plot {datetime} -- The date from which the plot starts
    """
    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 4))
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Demande Electrique (kWh)')
    ax1.set_title('3 jours de demande électrique')

    to_plot = lt_1213.customers[0].GC[(day_begin_plot-DATA_BEGIN) // ONE_STEP : (day_begin_plot-DATA_BEGIN) // ONE_STEP + 3 * 48]
    dates = [day_begin_plot + i * ONE_STEP for i in range(3*48)]
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d - %Hh'))

    plt.plot(dates, to_plot, color="Blue")
    plt.grid(True)
    plt.show()

def plot_net_demand(day_begin_plot):
    """Plots 3 days of net demand
    
    Arguments:
        day_begin_plot {datetime} -- The date from which the plot starts
    """
    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 4))
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Demande Nette (kWh)')
    ax1.set_title('3 jours de demande nette')

    to_plot = lt_1213.customers[0].net_load[(day_begin_plot-DATA_BEGIN) // ONE_STEP : (day_begin_plot-DATA_BEGIN) // ONE_STEP + 3 * 48]
    dates = [day_begin_plot + i * ONE_STEP for i in range(3*48)]
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d - %Hh'))

    plt.plot(dates, to_plot, color="Blue")
    plt.grid(True)
    plt.show()

def plot_generation(day_begin_plot):
    """Plots 3 days of electric generation with the solar pannel
    
    Arguments:
        day_begin_plot {datetime} -- The date from which the plot starts
    """
    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 4))
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Generation Electrique (kWh)')
    ax1.set_title('3 jours de génération électrique')

    to_plot = lt_1213.customers[0].GG[(day_begin_plot-DATA_BEGIN) // ONE_STEP : (day_begin_plot-DATA_BEGIN) // ONE_STEP + 3 * 48]
    dates = [day_begin_plot + i * ONE_STEP for i in range(3*48)]
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d - %Hh'))

    plt.plot(dates, to_plot, color="Blue")
    plt.grid(True)
    plt.show()

def plot_prices(day_begin_plot):
    """Plots the prices in the microgrid
    
    Arguments:
        day_begin_plot {datetime} -- The date from which the plot starts
    """
    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 4))
    ax1.set_xlabel('Heure')
    ax1.set_ylabel('Prix (\u20ac/kWh)')
    ax1.set_title('Tarification de l\'électricité')

    dates = [day_begin_plot + i * ONE_STEP for i in range(48)]
    dates.insert(12, dates[12])
    dates.insert(45, dates[44])

    purchase = np.insert(P_PURCHASE, 12, P_PURCHASE[11])
    purchase = np.insert(purchase, 45, purchase[45])


    plt.plot(dates, purchase, Color="Blue", label = "Import Prices")
    plt.plot([day_begin_plot + i * ONE_STEP for i in range(48)], P_SALE, Color="Orange", label = "Export Prices")
    plt.plot([day_begin_plot + i * ONE_STEP for i in range(48)], P_PURCHASE, Color="Orange", label = "Export Prices")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
    plt.grid(True)
    plt.show()

def plot_correlogram_net_demand():
    """Plots the autocorrelogram of the net demand
    """
    fig, ax= plt.subplots(1, 1, figsize=(18, 5))
    plot_acf(lt_1213.customers[0].net_load, ax, title="Autocorrélogramme de l'échantillon (calculé sur un an)", lags=48*10)
    plt.show()

def plot_battery_time(i, x_forecast_memory, net_demand_forecast_memory, last_x_memory, last_net_demand_memory):
    """Plots the net_demand (past and prediction) and the battery charge(past and prediction) for several days
    
    Arguments:
        i {int} -- index of the day where begins the plot
        x_forecast_memory {np.array} -- loaded version of"save/x_forecast_memory.npy"
        net_demand_forecast_memory {np.array} -- loaded version of"save/net_demand_forecast_memory.npy"
        last_x_memory {np.array} -- loaded version of "save/last_x_memory.npy"
        last_net_demand_memory {np.array} -- loaded version of "save/last_net_demand_memory.npy"
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 11))

    ax1.set_ylabel("Demande nette (kWh)")

    instant = DAY_BEGIN + i * ONE_STEP

    net_demand_forecast = net_demand_forecast_memory[i,:]
    previous_net_demand = last_net_demand_memory[i,:]


    ax1.plot([instant + k * ONE_STEP for k in range(len(net_demand_forecast))], net_demand_forecast, color="DarkOrange", label="Prédiction")
    ax1.plot([instant + (- 5*48 + k) * ONE_STEP for k in range(len(previous_net_demand))], previous_net_demand, color="Blue", label="Passé")
    ax1.set_title("Demande nette passée et prédite le " + instant.strftime("%m/%d/%Y à %H:%M"))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()
    ax1.legend(bbox_to_anchor=(0.8, 0.8))

    x_forecast = x_forecast_memory[i,:]
    previous_x = last_x_memory[i,:]

    ax2.set_ylim(-0.1, 6)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Charge (kWh)")

    ax2.plot([instant + k * ONE_STEP for k in range(len(x_forecast))], x_forecast, color="DarkOrange", label="Prediction")
    ax2.plot([instant + (k - 5 * 48) * ONE_STEP for k in range(len(previous_x))], previous_x, color="Blue", label="Passé")
    ax2.set_title("Trajectoire de la charge le " + instant.strftime("%m/%d/%Y à %H:%M"))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d - %Hh'))
    ax2.legend(bbox_to_anchor=(0.8, 0.8))
    plt.show()

def plot_battery_one_day(i, x_forecast_memory, net_demand_forecast_memory):
    """Plots the net_demand (past and prediction) and the battery charge(past and prediction) for one_day
    
    Arguments:
        i {int} -- index of the day where begins the plot
        x_forecast_memory {np.array} -- loaded version of"save/x_forecast_memory.npy"
        net_demand_forecast_memory {np.array} -- loaded version of"save/net_demand_forecast_memory.npy"
        last_x_memory {np.array} -- loaded version of "save/last_x_memory.npy"
        last_net_demand_memory {np.array} -- loaded version of "save/last_net_demand_memory.npy"
    """

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 11))

    ax1.set_ylabel("Demande nette (kWh)")

    instant = DAY_BEGIN + i * ONE_STEP

    net_demand_forecast = net_demand_forecast_memory[i,:]
    previous_net_demand = last_net_demand_memory[i,:]


    ax1.plot([instant + k * ONE_STEP for k in range(48)], net_demand_forecast[:48], color="DarkOrange", label="Prédiction")
    ax1.set_title("Demande nette prédite le " + instant.strftime("%m/%d/%Y à %H:%M"))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()


    x_forecast = x_forecast_memory[i,:]
    previous_x = last_x_memory[i,:]

    ax2.set_ylim(-0.1, 6)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Charge (kWh)")

    ax2.plot([instant + k * ONE_STEP for k in range(48)], x_forecast[:48], color="DarkOrange", label="Prediction")
    ax2.set_title("Trajectoire de la charge prescrite le " + instant.strftime("%m/%d/%Y à %H:%M"))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d - %Hh'))
    plt.show()


def plot_battery(x_forecast_memory, net_demand_forecast_memory, last_x_memory, last_net_demand_memory):
    """Plots the net_demand (past and prediction) and the battery charge(past and prediction) evolution with an animation
    
    Arguments:
        i {int} -- index of the day where begins the plot
        x_forecast_memory {np.array} -- loaded version of"save/x_forecast_memory.npy"
        net_demand_forecast_memory {np.array} -- loaded version of"save/net_demand_forecast_memory.npy"
        last_x_memory {np.array} -- loaded version of "save/last_x_memory.npy"
        last_net_demand_memory {np.array} -- loaded version of "save/last_net_demand_memory.npy"
    """

    fig1, ax1 = plt.subplots(1, 1, figsize=(18, 5))
    line_forecast1, = ax1.plot([], [], color="DarkOrange")
    line_past1, = ax1.plot([],[], color="Blue")
    title1 = ax1.text(0.5, 1, "", transform=ax1.transAxes, alpha = 1, ha="center")

        #ax1.set_xlim(0,14 * 48)
    ax1.set_xlim(-5 * 48, 14 * 48)
    ax1.set_ylim(-0.1, 6)
    ax1.set_xlabel('Pas de temps')
    ax1.set_ylabel('Génération Electrique (kWh)')
    #ax1.set_title('Chargement de la batterie')
    #plt.legend(bbox_to_anchor=(0.8, 0.8))

    lines1 = [title1, line_forecast1, line_past1]

    def init1():
        lines1[1].set_data([], [])
        lines1[2].set_data([], [])
        lines1[0].set_text("")
        return lines1

    fig2, ax2 = plt.subplots(1, 1, figsize=(18, 5))
    line_forecast2, = ax2.plot([], [], color="DarkOrange")
    line_past2, = ax2.plot([],[], color="Blue")

    #ax2.set_xlim(0,14 * 48)
    ax2.set_ylim(-3, 3)
    ax2.set_xlabel('Pas de temps')
    ax2.set_ylabel('Génération Electrique (kWh)')
    #ax2.set_title('Prédiction de la demande nette')
    #plt.legend(bbox_to_anchor=(0.8, 0.8))
    title2 = ax2.text(0.5, 1, "", transform=ax1.transAxes, ha="center")

    lines2 = [title2, line_forecast2, line_past2]

    def animate1(i):
        print(i, " begin")

        instant = DAY_BEGIN + i * ONE_STEP
        x_forecast = x_forecast_memory[i,:]
        previous_x = last_x_memory[i,:]
        #ax1.set_xlim(instant - 5 * 48 * ONE_STEP, instant + 14 * 48 * ONE_STEP)
        lines1[1].set_data([int((k * ONE_STEP).total_seconds()) // 1800 for k in range(len(x_forecast))], x_forecast)
        lines1[2].set_data([int((k * ONE_STEP).total_seconds()) // 1800 - 5 *48 for k in range(len(previous_x))], previous_x)
        lines1[0].set_text("Trajectoire de la charge le " + instant.strftime("%m/%d/%Y à %H:%M"))

        return lines1


    def animate2(i):
        print(i, " begin")

        instant = DAY_BEGIN + i * ONE_STEP
        net_demand_forecast = net_demand_forecast_memory[i,:]
        previous_net_demand = last_net_demand_memory[i,:]

        #ax2.set_xlim(instant - 5 * 48 * ONE_STEP, instant + 14 * 48 * ONE_STEP)

        title2.set_text(instant.strftime("%m/%d/%Y, %H:%M"))
        ax2.set_xlim(-5 * 48, 14 * 48)
        lines2[1].set_data([ int((k * ONE_STEP).total_seconds()) // 1800 for k in range(len(net_demand_forecast))], net_demand_forecast)
        lines2[2].set_data([ int((k * ONE_STEP).total_seconds()) // 1800 - 5 *48 for k in range(len(previous_net_demand))], previous_net_demand)
        lines2[0].set_text("Demande nette passée et prédite le " + instant.strftime("%m/%d/%Y à %H:%M"))
        return lines2

    ani = [
        animation.FuncAnimation(fig=fig1, func=animate1, init_func=init1, frames=(DAY_END - DAY_BEGIN) // ONE_STEP, interval=100, repeat=False, blit=True),
        animation.FuncAnimation(fig=fig2, func=animate2, frames=(DAY_END - DAY_BEGIN) // ONE_STEP, interval=100, repeat=False, blit=True)
        ]

    plt.show()

    ani[0].save('save/myAnimation.gif', writer='imagemagick', fps=30)

def plot_cost(u):
    """Plot the cumulative costs of the 3 tested methods for 1 month
    
    Arguments:
        u {float array} -- the energy transiting in the electric cable
    """

    p_buy_30, p_sell_30 = forecast_prices(DAY_BEGIN, P_PURCHASE, P_SALE, step=ONE_STEP, n_days=30)

    cost_without_battery = evaluate_without_battery(
        p_sell=p_sell_30,
        p_buy=p_buy_30,
        net_demand=lt_1213.customers[0].net_load[(DAY_BEGIN-DATA_BEGIN) // ONE_STEP : (DAY_BEGIN-DATA_BEGIN) // ONE_STEP + 30 * 48]
    )

    cost_clairvoyant = evaluate_clairvoyant(
        p_sell=p_sell_30,
        p_buy=p_buy_30,
        net_demand=lt_1213.customers[0].net_load[(DAY_BEGIN-DATA_BEGIN) // ONE_STEP : (DAY_BEGIN-DATA_BEGIN) // ONE_STEP + 30 * 48 + 1]
    )

    cost = evaluate(
        p_sell=p_sell_30,
        p_buy=p_buy_30,
        u=u,
        net_demand=lt_1213.customers[0].net_load[(DAY_BEGIN-DATA_BEGIN) // ONE_STEP : (DAY_BEGIN-DATA_BEGIN) // ONE_STEP + 30 * 48 + 1]
        )
    fig, ax = plt.subplots(1,1)
    ax.plot([DAY_BEGIN + k * ONE_STEP for k in range(len(cost_without_battery))], cost_without_battery, color="Green", label="Sans batterie")
    ax.plot([DAY_BEGIN + k * ONE_STEP for k in range(len(cost))], cost, color="Blue", label="Commande prédictive")
    ax.plot([DAY_BEGIN + k * ONE_STEP for k in range(len(cost_clairvoyant))], cost_clairvoyant, color="Red", label="Cas clairvoyant")
    ax.set_title("Evolution du prix cumulatif de la microgrid")
    ax.set_xlabel("Date")
    ax.set_ylabel("Coût (\u20ac)")
    ax.legend(bbox_to_anchor=(0.8, 0.8))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()
    plt.show()

    print(cost_clairvoyant[-1], cost[-1], cost_without_battery[-1])


if __name__ == "__main__":

    #plot_demand(DAY_BEGIN + 3 * 48 * ONE_STEP)
    #plot_generation(DAY_BEGIN + 3 * 48 * ONE_STEP)
    #plot_prices(DAY_BEGIN)
    #plot_net_demand(DAY_BEGIN + 3 * 48 * ONE_STEP)
    #plot_correlogram_net_demand()

    x_forecast_memory = np.load("save/x_forecast_memory.npy")
    net_demand_forecast_memory = np.load("save/net_demand_forecast_memory.npy")
    last_x_memory = np.load("save/last_x_memory.npy")
    last_net_demand_memory = np.load("save/last_net_demand_memory.npy")
    u = np.load("save/u.npy")

    #plot_battery(x_forecast_memory, net_demand_forecast_memory, last_x_memory, last_net_demand_memory)
    plot_battery_time(8 * 48, x_forecast_memory, net_demand_forecast_memory, last_x_memory, last_net_demand_memory)
    #plot_battery_one_day(2 * 48, x_forecast_memory, net_demand_forecast_memory)
    #plot_cost(u)
