# -*- coding: utf-8 -*-
"""Smoothing Model for Competition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1S4CU8E4hC5sXWJHo3lb2A8zC2kHaMgnq
"""

import pandas as pd
import numpy as np
from plotnine import *
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn import tree
from sklearn import metrics
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy.stats as ss
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from sklearn.model_selection import train_test_split

df = pd.read_csv('https://raw.githubusercontent.com/laneyhlc/DSO424/main/CompetitionData.csv')

df['Date'] = pd.to_datetime(df['Date'])

df['Year']= df['Date'].dt.year
df['Month']= df['Date'].dt.month
df['Day']= df['Date'].dt.day
df['Hour']= df['Date'].dt.hour
df['Time']= list(range(1,len(df)+1))

df.loc[df['Year']<2012]

df

df.iloc[35063-24*365]

"""EXPONENTIAL SMOOTHING  

Training set (Before): start = 01/2008, end=12/2011 [35063]

Testing set (After): start = 01/2012, end=12/2012[35064-43847]
"""

M1 = ExponentialSmoothing(df.loc[:35063-24*365, 'Load'], seasonal = 'add', seasonal_periods=24).fit()

M1.summary()

M1.forecast(8784+8760)

df['M1'] = np.nan

df.loc[:35063-24*365,'M1'] = M1.fittedvalues

df.loc[35064-24*365:,'M1'] = M1.forecast(8784+8760)

df['Prediction'] = 'Fitted values'
df.loc[35064-24*365:,'Prediction'] = 'Forecast'

def rmse(actual,predicted):
    return round(((actual - predicted)**2).mean()**0.5,2)

def mape(actual,predicted):
    return round(abs((actual - predicted)/actual).mean()*100,2)

def accuracy(actual,predicted,h=0):
    n_train = len(actual) - h
    accuracy_metrics = pd.DataFrame(columns=['RMSE','MAPE(%)'],index=['Training set','Testing set'])
    accuracy_metrics.loc['Training set','RMSE'] = rmse(actual[:n_train],predicted[:n_train])
    accuracy_metrics.loc['Training set','MAPE(%)'] = mape(actual[:n_train],predicted[:n_train])
    if (h>0):
        accuracy_metrics.loc['Testing set','RMSE'] = rmse(actual[n_train:],predicted[n_train:])
        accuracy_metrics.loc['Testing set','MAPE(%)'] = mape(actual[n_train:],predicted[n_train:])
    return accuracy_metrics

accuracy(actual = df.loc[:35064,'Load'], predicted = df.loc[:35064,'M1'],h=8760)