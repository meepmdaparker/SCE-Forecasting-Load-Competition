# -*- coding: utf-8 -*-
"""CaseComp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UQnLt0tmcKOYrXgqxRlO21juyPXopN-r
"""

import pandas as pd
import numpy as np
from plotnine import *
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn import metrics

import datetime as dt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf

from statsmodels.tsa.api import ExponentialSmoothing

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA

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

df = pd.read_csv('https://raw.githubusercontent.com/laneyhlc/DSO424/main/CompetitionData.csv')

df['Date']= pd.to_datetime(df['Date'])

df['Year']=df['Date'].dt.year
df['Month']=df['Date'].dt.month
df['Weekday']=df['Date'].dt.weekday
df['Day']=df['Date'].dt.day
df['Hour']=df['Date'].dt.hour

df['Time']=list(range(1,len(df)+1))

(
    ggplot(df[:35064],aes('Time','Temperature')) + geom_point() + geom_line() + theme(figure_size=(40,15))

)

(
    ggplot(df[:35064],aes('Time','Load')) + geom_point() + geom_line() + theme(figure_size=(40,15))

)

df['LoadBefore']= df['Load']

M1 = smf.ols('LoadBefore ~ Temperature', data = df[:35064]).fit()

M1.summary()

df['M1']=M1.fittedvalues
df['M1residuals'] = M1.resid

(
    ggplot(df[:35064],aes('Time','LoadBefore')) + geom_point() + geom_line() + theme(figure_size=(40,15))
    + geom_point(df[:35064],aes('Time','M1'),color='blue') +  geom_line(df[:35064],aes('Time','M1'),color='blue')

)

M2 = smf.ols('LoadBefore ~ Temperature + Time + C(Month) + C(Day)+ C(Weekday) + C(Hour)', data = df[:35064]).fit()

df['M2']=M2.fittedvalues
df['M2residuals'] = M2.resid

(
    ggplot(df[:35064],aes('Time','LoadBefore')) + geom_point() + geom_line() + theme(figure_size=(40,15))
    + geom_point(df[:35064],aes('Time','M2'),color='blue') +  geom_line(df[:35064],aes('Time','M2'),color='blue')

)

plot_acf(df['M2residuals'],missing='drop',zero=False);
plot_pacf(df.loc[df['M2residuals'].notna(),'M2residuals'],zero=False,lags=50);

df['LoadBeforeLag1'] = df['LoadBefore'].shift(1)
df['LoadBeforeLag2'] = df['LoadBefore'].shift(2)

#M3:
# Training=2008, Testing=2009
M3 = smf.ols('LoadBefore ~ Temperature + C(Month) + C(Day)+ C(Weekday) + C(Hour) + LoadBeforeLag1 + LoadBeforeLag2', data = df[:8784]).fit()

df['M3']=M3.fittedvalues
df['M3residuals'] = M3.resid

plot_acf(df['M3residuals'],missing='drop',zero=False);

for i in list(range(8784,8784+24*365)):
    df.loc[[i],'LoadBeforeLag1'] = df.loc[[i-1],'LoadBefore'].values
    df.loc[[i],'LoadBeforeLag2'] = df.loc[[i-2],'LoadBefore'].values   
    df.loc[[i],'LoadBefore'] = M3.predict(df.loc[[i]]).values
    df.loc[[i],'M3'] = M3.predict(df.loc[[i]]).values

# Training=2008, Testing=2009
accuracy(actual = df.loc[:8784+24*365,'Load'], 
         predicted = df.loc[:8784+24*365,'M3'],h=24*365)

(
    ggplot(df[:8784+24*365],aes('Time','LoadBefore')) + geom_point() + geom_line() + theme(figure_size=(40,15))
    + geom_point(df[:8784+24*365],aes('Time','M3'),color='blue') +  geom_line(df[:8784+24*365],aes('Time','M3'),color='blue')

)

#M4:
# Training=2008,2009, Testing=2010
M4 = smf.ols('LoadBefore ~ Temperature + C(Month) + C(Day) + C(Weekday) + C(Hour) + LoadBeforeLag1 + LoadBeforeLag2', data = df[:8784+24*365]).fit()
df['M4']=M4.fittedvalues
df['M4residuals'] = M4.resid

for i in list(range(8784+24*365,8784+24*365*2)):
    df.loc[[i],'LoadBeforeLag1'] = df.loc[[i-1],'LoadBefore'].values
    df.loc[[i],'LoadBeforeLag2'] = df.loc[[i-2],'LoadBefore'].values  
    df.loc[[i],'LoadBefore'] = M4.predict(df.loc[[i]]).values
    df.loc[[i],'M4'] = M4.predict(df.loc[[i]]).values

# Training=2008,2009, Testing=2010
accuracy(actual = df.loc[:8784+24*365*2-1,'Load'], 
         predicted = df.loc[:8784+24*365*2-1,'M4'],h=24*365)

(
    ggplot(df[:8784+24*365*2],aes('Time','LoadBefore')) + geom_point() + geom_line() + theme(figure_size=(40,15))
    + geom_point(df[:8784+24*365*2],aes('Time','M4'),color='blue') +  geom_line(df[:8784+24*365*2],aes('Time','M4'),color='blue')

)

#M5: 
# Training=2008,2009,2010, Testing=2011
M5 = smf.ols('LoadBefore ~ Temperature:C(Hour) + Temperature**2:C(Hour) + Temperature**3:C(Hour) + Temperature:C(Month) + Temperature**2:C(Month) + Temperature**3:C(Month) + Time + C(Month) + C(Weekday) + C(Weekday):C(Hour) + LoadBeforeLag1 + LoadBeforeLag2', data = df[:8784+24*365*2]).fit()
df['M5']=M5.fittedvalues
df['M5residuals'] = M5.resid

for i in list(range(8784+24*365*2,8784+24*365*3)):
    df.loc[[i],'LoadBeforeLag1'] = df.loc[[i-1],'LoadBefore'].values
    df.loc[[i],'LoadBeforeLag2'] = df.loc[[i-2],'LoadBefore'].values   
    df.loc[[i],'LoadBefore'] = M5.predict(df.loc[[i]]).values
    df.loc[[i],'M5'] = M5.predict(df.loc[[i]]).values

# Training=2008,2009,2010, Testing=2011
accuracy(actual = df.loc[:8784+24*365*3-1,'Load'], 
         predicted = df.loc[:8784+24*365*3-1,'M5'],h=24*365)

(
    ggplot(df[:8784+24*365*3],aes('Time','LoadBefore')) + geom_point() + geom_line() + theme(figure_size=(40,15))
    + geom_point(df[:8784+24*365*3],aes('Time','M5'),color='blue') +  geom_line(df[:8784+24*365*3],aes('Time','M5'),color='blue')

)

#M6: All Data
M6 = smf.ols('LoadBefore ~ Temperature:C(Hour) + Temperature**2:C(Hour) + Temperature**3:C(Hour) + Temperature:C(Month) + Temperature**2:C(Month) + Temperature**3:C(Month) + Time + C(Month) + C(Weekday):C(Hour) + LoadBeforeLag1 + LoadBeforeLag2', data = df[:35064]).fit()
df['M6']=M6.fittedvalues
df['M6residuals'] = M6.resid

for i in list(range(35064,len(df))):
    df.loc[[i],'LoadBeforeLag1'] = df.loc[[i-1],'LoadBefore'].values
    df.loc[[i],'LoadBeforeLag2'] = df.loc[[i-2],'LoadBefore'].values   
    df.loc[[i],'LoadBefore'] = M6.predict(df.loc[[i]]).values
    df.loc[[i],'M6'] = M6.predict(df.loc[[i]]).values

(
    ggplot(df,aes('Time','Load')) + geom_point() + geom_line() + theme(figure_size=(40,15))
    + geom_point(df,aes('Time','M6'),color='blue') +  geom_line(df,aes('Time','M6'),color='blue')
    + geom_point(df[35065:],aes('Time','M6'),color='purple') +  geom_line(df[35065:],aes('Time','M6'),color='purple')
    + geom_vline(xintercept=35065,size=3,color='green')
)
