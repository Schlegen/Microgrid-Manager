import matplotlib.pyplot as plt
import os
from random import randint
current_path = os.path.abspath('')
path_to_data = path_to_data = os.path.join(current_path, "data.csv")
import pandas as pd
import numpy as np
from copy import copy
from numpy.fft import fft, ifft
from datetime import date, datetime, timedelta, timezone
import re
import json

plt.style.use('fivethirtyeight')

#------------------CLASSES CUSTOMER AND DATAFRAMES -----------------------------

class Customer():
    def __init__(self, id, GC_customer=None, GG_customer=None):
        self.ID = id

        self.GC = np.array([])
        self.GG = np.array([])

        if GC_customer is not None:

            for k in range(len(GC_customer.index)):

                self.GC = np.concatenate((
                    self.GC,
                    GC_customer[["0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30", "4:00", "4:30", "5:00", "5:30",
                          "6:00", "6:30", "7:00", "7:30", "8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30",
                          "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
                          "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30",
                          "23:00", "23:30", "0:00"]].iloc[k].to_numpy()),
                    axis = 0
                )
        if GG_customer is not None:

            for k in range(len(GC_customer.index)):

                self.GG = np.concatenate((
                    self.GG,
                    GG_customer[["0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30", "4:00", "4:30", "5:00", "5:30",
                          "6:00", "6:30", "7:00", "7:30", "8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30",
                          "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
                          "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30",
                          "23:00", "23:30", "0:00"]].iloc[k].to_numpy()),
                    axis = 0
                )

        self.net_load = self.GC - self.GG

    def set_GC(self, new_GC):
        self.GC = copy(new_GC)

    def set_GG(self, new_GG):
        self.GG = copy(new_GG)

    def set_net_load(self):
        self.net_load = self.GC - self.GG

    def plot_GC(self, i, j=None):
        """
        i is an int in {0,..., 364}
        When it is note None, j is an int in {0,...364}
        When j is None the method plots the consumption of the customer during the ith day of the year,
        else, it plots the consumption of the customers between the ith day and the jth day included
        """
        if j is None:
            j = i #we plot only one day
        elif j < i:
            swap = j
            j = i
            i = swap
        fig, ax= plt.subplots(1, 1, figsize=(18, 5))
        time = [k for k in range(48*(j-i+1))]
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(time, self.GC[i*48:(j+1)*48])
        plt.grid(True)
        plt.show()

    def plot_GG(self, i, j=None):
        """
        i is an int in {0,..., 364}
        When it is note None, j is an int in {0,...364}
        When j is None the method plots the electric generation of the customer during the ith day of the year,
        else, it plots the consumption of the customers between the ith day and the jth day included
        """
        if j is None:
            j = i #we plot only one day
        elif j < i:
            swap = j
            j = i
            i = swap
        fig, ax= plt.subplots(1, 1, figsize=(18, 5))
        time = [k for k in range(48*(j-i+1))]
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(time, self.GG[i*48:(j+1)*48])
        plt.grid(True)
        plt.show()

    def plot_net_load(self, i, j=None):
        """
        i is an int in {0,..., 364}
        When it is note None, j is an int in {0,...364}
        When j is None the method plots the electric generation of the customer during the ith day of the year,
        else, it plots the consumption of the customers between the ith day and the jth day included
        """
        if j is None:
            j = i #we plot only one day
        elif j < i:
            swap = j
            j = i
            i = swap
        fig, ax= plt.subplots(1, 1, figsize=(18, 5))
        time = [k for k in range(48*(j-i+1))]
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(time, self.net_load[i*48:(j+1)*48])
        plt.grid(True)
        plt.show()

    def plot_fft_GG(self):
        """
        """
        # Number of sample points
        N = len(self.GG)
        # sample spacing
        T = 0.5
        yf = fft(self.GG)
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
        plt.grid()
        plt.show()

    def smooth1_GG(self, day1, f_lim, day2 = None):
        """
        day1 is an int in {0, ..., 364}
        f_lim is a float in [0;1]
        When it is not None, day2 is an int in {0, ..., 364}

        plots a smoothed curve corresponding self.GG by cuting high frequences in the spectral decompostion
        """

        N = len(self.GG)
        # sample spacing
        T = 0.5
        yf = fft(self.GG)
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

        i = N//2- 1
        while xf[i] > f_lim and i >= 0:
            yf[i] = 0
            i -= 1

        new_GG = ifft(yf)

        if day2 is None:
            day2 = day1 #we plot only one day
        elif day2 < day1:
            swap = day2
            day2 = day1
            day1 = swap
        figure = plt.figure()
        axes = figure.add_subplot(111)
        time = [k for k in range(48*(day2-day1+1))]
        axes.xaxis.set_ticks_position('bottom')
        plt.plot(time, new_GG[day1*48:(day2+1)*48])
        plt.grid()
        plt.show()

    def smooth2_GG(self, day1, threshold, day2 = None):
        """
        day1 is an int in {0, ..., 364}
        threshold is a float in [0;1]
        When it is not None, day2 is an int in {0, ..., 364}

        plots a smoothed curve corresponding self.GG by cuting frequences
        which coefficients ion the spectral decompostion is lower than threshold
        """
        # Number of sample points
        N = len(self.GG)
        # sample spacing
        T = 0.5
        yf = fft(self.GG)
        for i in range(N//2):
            if  2.0/N * abs(yf[i]) < threshold:
                yf[i] = 0
        new_GG = ifft(yf)

        if day2 is None:
            day2 = day1 #we plot only one day
        elif day2 < day1:
            swap = day2
            day2 = day1
            day1 = swap
        figure = plt.figure()
        axes = figure.add_subplot(111)
        time = [k for k in range(48*(day2-day1+1))]
        axes.xaxis.set_ticks_position('bottom')
        plt.plot(time, new_GG[day1*48:(day2+1)*48])
        plt.grid()
        plt.show()

    def plot_fft_GC(self):
        """
        """
        # Number of sample points
        N = len(self.GC)
        # sample spacing
        T = 0.5
        yf = fft(self.GC)
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
        plt.grid()
        plt.show()

    def smooth1_GC(self, day1, f_lim, day2 = None):
        """
        day1 is an int in {0, ..., 364}
        f_lim is a float in [0;1]
        When it is not None, day2 is an int in {0, ..., 364}

        plots a smoothed curve corresponding self.GC by cuting high frequences in the spectral decompostion
        """

        N = len(self.GC)
        # sample spacing
        T = 0.5
        yf = fft(self.GC)
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

        i = N//2- 1
        while xf[i] > f_lim and i >= 0:
            yf[i] = 0
            i -= 1

        new_GC = ifft(yf)

        if day2 is None:
            day2 = day1 #we plot only one day
        elif day2 < day1:
            swap = day2
            day2 = day1
            day1 = swap
        figure = plt.figure()
        axes = figure.add_subplot(111)
        time = [k for k in range(48*(day2-day1+1))]
        axes.xaxis.set_ticks_position('bottom')
        plt.plot(time, new_GC[day1*48:(day2+1)*48])
        plt.grid()
        plt.show()

    def smooth2_GC(self, day1, threshold, day2 = None):
        """
        day1 is an int in {0, ..., 364}
        threshold is a float in [0;1]
        When it is not None, day2 is an int in {0, ..., 364}

        plots a smoothed curve corresponding self.GC by cuting frequences
        which coefficients ion the spectral decompostion is lower than threshold
        """
        # Number of sample points
        N = len(self.GC)
        # sample spacing
        T = 0.5
        yf = fft(self.GC)
        for i in range(N//2):
            if  2.0/N * abs(yf[i]) < threshold:
                yf[i] = 0
        new_GC = ifft(yf)

        if day2 is None:
            day2 = day1 #we plot only one day
        elif day2 < day1:
            swap = day2
            day2 = day1
            day1 = swap
        figure = plt.figure()
        axes = figure.add_subplot(111)
        time = [k for k in range(48*(day2-day1+1))]
        axes.xaxis.set_ticks_position('bottom')
        plt.plot(time, new_GC[day1*48:(day2+1)*48])
        plt.grid()
        plt.show()

    def write_line(self):
        """
        Write the line that will be written in the file where the data frame will be stored
        """
        #First, we save the id of the customer, then the length of the measure

        string_row = str(self.ID) + " " + str(len(self.GG))

        #Then we stock all the values (GG first then GC)
        for i in self.GG:
            string_row += " " + str(i)

        for i in self.GC:
            string_row += " " + str(i)

        return string_row

class DataFrame():
    """A dataframe is a list of customers
    """
    def __init__(self, df=None):
        """
        -line is a string that represents a line of the csv file
        build the data according to a line of the .svg file
        """

        self.customers = []

        if df is not None:
            GC = df[df.ConsumptionCategory == 'GC']
            GG = df[df.ConsumptionCategory == 'GG']
            for i in range(1, df['Customer'].nunique()+1):
                GC_customer = GC[GC.Customer == i]
                GG_customer = GG[GG.Customer == i]
                self.customers.append(Customer(i, GC_customer, GG_customer))

    def set_customers(self, new_customers):
        """
        """
        self.customers = copy(new_customers)

    def plot_GC(self, id_customer, day1, day2=None):
        """
        day1 is an int in {0, ..., 364}
        When it is note None, day2 is an int in {0, ..., 364}
        When j is None the method plots the consumption of the customer with id_consumer during the ith day of the year,
        else, it plots the consumption of the customers between the ith day and the jth day included
        """
        self.customers[id_customer].plot_GC(day1, day2)

    def plot_GG(self, id_customer, day1, day2=None):
        """
        i is an int in {0,..., 364}
        When it is note None, j is an int in {0,...364}
        When j is None the method plots the electric generation of the customer during the ith day of the year,
        else, it plots the generation of the customers between the ith day and the jth day included
        """
        self.customers[id_customer].plot_GG(day1, day2)

    def plot_net_load(self, id_customer, day1, day2=None):
        """

        """
        self.customers[id_customer].plot_net_load(day1, day2)


    def store(self, file_name):
        """
        store the datacenter in a .txt file
        """
        with open(file_name,'w') as f:
            for i in range(len(self.customers)):
                string_row = self.customers[i].write_line()+'\n'
                f.write(string_row)

## --------------------Aquisition des données ---------------------------------

def acquisition(path_to_data):
    """
    -name_file is a string that represents the adress of a file
    returns the DataFrame object associated to the .csv
    """
    l_t = pd.read_csv(path_to_data, skiprows=1)
    return DataFrame(l_t)

def load_data_frame(name_file):
    """
    -name_file is a .txt file
    returns the data_frame from the informations in the .txt file
    """

    def load_customer(string_row):
        row = string_row.split(' ')
        ID = int(row[0])
        len_measure = int(row[1])
        GG = np.array([0.0 for i in range(len_measure)])
        GC = np.array([0.0 for i in range(len_measure)])
        for i in range(2, 2 + len_measure):
            GG[i - 2] = float(row[i])
        for i in range(2 + len_measure, 2 + 2*len_measure):
            GC[i - 2 - len_measure] = float(row[i])
        customer = Customer(ID)
        customer.set_GG(GG)
        customer.set_GC(GC)
        customer.set_net_load()
        return customer

    customers = []
    with open(name_file,'r') as f:
        for line in f.readlines():
            customers.append(load_customer(line))
            df = DataFrame()
            df.set_customers(customers)
        return df

## --------------------------- Outils numériques -------------------------------

def dist_square(test, predict):
    n = len(test)
    sum_square = 0
    for i in range(n):
        sum_square += (test[i] - predict[i])**2
    return(sum_square / n)

## --------------------------- Stockage des resultats -------------------------
def to_string(tab):
    rep ="["

    for e in tab :

        rep += str(e) + " "

    return (rep + "]")


def take_list_values(string):
    string_without_succesive_spaces = re.sub(' +', ' ', string)

    if string_without_succesive_spaces[-2] == " ":
        last = -2
    else:
        last = -1

    if string_without_succesive_spaces[1] == " ":
        first = 2
    else:
        first = 1

    return([float(e) for e in string_without_succesive_spaces[first:last].split(" ")])

class SaveFit:

    def __init__(self, string=None, key=None, MSE=None, ar_param=None, ma_param=None, seasonal_ar_param=None, seasonal_ma_param=None, time_train=None, time_test=None):

        if string == None:
            self.key = key
            self.MSE = MSE
            self.ar_param = ar_param
            self.ma_param = ma_param
            self.seasonal_ar_param = seasonal_ar_param
            self.seasonal_ma_param = seasonal_ma_param
            self.time_train = time_train
            self.time_test = time_test

        else:
            #print(string)
            values = string.split("; ")
            self.key = values[0]
            self.MSE = float(values[1])
            if len(values[2]) > 2:
                self.ar_param = take_list_values(values[2]) #[float(e) for e in values[2][1:-1].split(" ")]
            else:
                self.ar_param = []
            if len(values[3]) > 2:
                self.ma_param = take_list_values(values[3]) # [float(e) for e in values[3][1:-1].split(" ")]
            else:
                self.ma_param = []
            if len(values[4]) > 2:
                self.seasonal_ar_param = take_list_values(values[4]) # [float(e) for e in values[4][1:-1].split(" ")]
            else:
                self.seasonal_ar_param = []
            if len(values[5]) > 2:
                self.seasonal_ma_param = take_list_values(values[5]) # [float(e) for e in values[5][1:-1].split(" ")]
            else:
                self.seasonal_ma_param = []
            self.time_train = float(values[6])
            self.time_test = float(values[7])


    def __str__(self):
        return(f"{self.key}; {self.MSE}; {to_string(self.ar_param)}; {to_string(self.ma_param)}; {to_string(self.seasonal_ma_param)}; {to_string(self.seasonal_ar_param)}; {self.time_train}; {self.time_test}" + '\n')

    def __repr__(self):
        return(f"{self.key}; {self.MSE}; {self.ar_param}; {self.ma_param}; {self.seasonal_ma_param}; {self.seasonal_ar_param}; {self.time_train}; {self.time_test}" + '\n')

def load_save_file(path_to_file="results_sarima.txt"):
    dico = {}
    with open(path_to_file,'r') as save_file:
        lines = save_file.readlines()
        for line in lines:
            #print(line)
            fit = SaveFit(string=line)
            dico[fit.key] = fit
    return(dico)

def save_fit_in_dico(fit, dico):
    dico[fit.key] = fit

def save_fit_in_txt(fit, path_to_file="results_sarima.txt"):
    with open(path_to_file,'a') as save_file:
        save_file.writelines([str(fit)])

## ----------------------- Recherche des meilleurs résultats ----------------------------

def get_param(key):
    return(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", key))

def sort_ARMA(dico):
    list_result = []
    for key in dico:
        params = get_param(key)
        if params[1] == '0' and params[3] == '0' and params[4] == '0' and params[5] == '0':
            list_result.append((key, dico[key].MSE))
    list_result.sort(key=lambda x : x[1])
    return(list_result)

def sort_ARIMA(dico):

    list_result = []
    for key in dico:
        params = get_param(key)
        if params[3] == '0' and params[4] == '0' and params[5] == '0':
            list_result.append((key, dico[key].MSE))
    list_result.sort(key=lambda x : x[1])
    return(list_result)

def sort_SARIMA(dico):

    list_result = []

    for key in dico :
        list_result.append((key, dico[key].MSE))

    list_result.sort(key=lambda x : x[1])
    return(list_result)

# stocker un tableau de time_series en jsonify

def time_series_to_json(time_series, series_begin, one_step, file_name):
    rep = [[(series_begin + i * one_step).replace(tzinfo=timezone.utc).timestamp()*1000, time_series[i]] for i in range(len(time_series))]
    with open(file_name, 'w') as json_file:
        json.dump(rep, json_file)
