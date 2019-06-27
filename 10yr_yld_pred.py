#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 18:07:20 2019

@author: jakekrafczyk
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model, metrics
from scipy.stats.stats import pearsonr

#assign datasets
copp = pd.read_csv('Copper Futures Historical Data (1).csv')
gold = pd.read_csv('WGC-GOLD_DAILY_USD.csv')
lqd = pd.read_csv('LQD.csv')
ief = pd.read_csv('IEF.csv')
iyf = pd.read_csv('IYF.csv')
idu = pd.read_csv('IDU.csv')
tenyr_yld = pd.read_csv('United States 10-Year Bond Yield Historical Data.csv')

#index by date and flip datasets to match
def index_date(data):
    data['Date'] = pd.to_datetime(data.Date)
    data.index = data['Date']
    data = data.drop(columns = "Date")
    return data

copp = index_date(copp)
copp = copp.reindex(index = copp.index[::-1])

gold = index_date(gold)
gold = gold.reindex(index = gold.index[::-1])

tenyr_yld = index_date(tenyr_yld)
tenyr_yld = tenyr_yld.reindex(index = tenyr_yld.index[::-1])

lqd = index_date(lqd)
ief = index_date(ief)
iyf = index_date(iyf)
idu = index_date(idu)

#concatenate datasets and eliminate dates that aren't available in all datasets
prices = [copp.Price,gold.Value,lqd.Close,ief.Close,iyf.Close,idu.Close,tenyr_yld.Price]

dataset = pd.concat(prices,axis=1,join='inner',ignore_index=True)
dataset.columns = ['Copper','Gold','LQD','IEF','IYF','IDU','10yr_yield']

#create predictive ratios
copp_gold = pd.DataFrame(dataset.Copper/dataset.Gold)
dataset['Copp_Gold'] = copp_gold    

lqd_ief = pd.DataFrame(dataset.LQD/dataset.IEF)
dataset['LQD_IEF'] = lqd_ief

iyf_idu = pd.DataFrame(dataset.IYF/dataset.IDU)
dataset['IYF_IDU'] = iyf_idu

#create weekly and monthly datasets
weekly_dataset = dataset.resample('W').max()
monthly_dataset = dataset.resample('M').max()

#define the dependent variable y
y_weekly = weekly_dataset['10yr_yield']
y_monthly = monthly_dataset['10yr_yield']

#define the independent variable X - must keep as dataframe for regr functions
X_weekly = weekly_dataset.iloc[:,7:8]
X_monthly = monthly_dataset.iloc[:,7:8]

#choose model and fit it
regr = linear_model.LinearRegression()

#define rolling regression function
def RollingOLS(X,y,window=int):
    #step 1- define windows start and end
    start = 0
    end = window
    
    #3- have dataframes ready
    accscores = pd.DataFrame()
    dateranges = pd.DataFrame()
    intercepts = pd.DataFrame()
    coefficients = pd.DataFrame()
    maescores = pd.DataFrame()
    R2scores = pd.DataFrame()
    pears_c = pd.DataFrame()
    p_values = pd.DataFrame()
   
    #run regressions on each window and get accscores back
    for x in range(len(X)):
        
        #define Y window
        ywin = y[int(start):int(end)]
        
        #define X window
        Xwin = X[int(start):int(end)]
        
        #define daterange
        startdate = str(ywin.index[0])
        startdate = startdate[:-9]
        enddate = str(ywin.index[-1])
        enddate = enddate[:-9]
        daterange = str(startdate + " to " + enddate)
        dateranges = pd.concat([dateranges, pd.DataFrame([daterange],columns=['Date Range'])],
                                                    axis=0,ignore_index=True)
        #fit the model to the window
        regr.fit(Xwin,ywin)
        
        #create index for predictions dataframe
        index1 = np.asarray([x for x in range(window)])
        
        #create predictions dataframe
        pred = pd.DataFrame(regr.predict(Xwin),
                          index=[index1],columns=['pred'])
        
        #creating the accuracy scores
        R2 = [metrics.r2_score(ywin,pred)]
        mean_ab_err = [metrics.mean_absolute_error(ywin,pred)]
        
        #transform data for scipy
        ywin = ywin.values
        Xwin = Xwin.iloc[:,0].values
        
        pear = [pearsonr(Xwin, ywin)]
        pear = list(pear[0])
        p_corr = [pear[0]]
        p_val = [pear[1]]
        
        #only need these for logistic regression
        #Cmatrix = confusion_matrix(ywin,pred)
        #rocauc = roc_auc_score(ywin,pred)
        
        #now storing them each in their own dataframe
        
        #intercepts - unnecessary for this analysis
        #intercepts = pd.concat([intercepts,pd.DataFrame([regr.intercept_],
        #                        columns=['Intercept'])],axis=0,ignore_index=True)
                                                                                    
        #coefficients - unnecessary for this analysis
        #coefficients = pd.concat([coefficients, pd.DataFrame(regr.coef_,
        #                        columns=['Coefficient'])],axis=0,ignore_index=True)
        
        #MAE
        maescores = pd.concat([maescores, pd.DataFrame(mean_ab_err,             
                                columns=['MAE'])],axis=0,ignore_index=True)
    
        #R2
        R2scores = pd.concat([R2scores, pd.DataFrame(R2,columns=['r2'])],
                              axis=0,ignore_index=True)
        
        #pearson correlation
        pears_c = pd.concat([pears_c, pd.DataFrame(p_corr,columns=['Pearson_Coef'])],
                              axis=0,ignore_index=True)
        
        #two tailed p-value
        p_values = pd.concat([p_values, pd.DataFrame(p_val,columns=['P-Value'])],
                              axis=0,ignore_index=True)
        #on to the next window
        start += 1
        end += 1
        
        if end > len(X):
            break
    
    #Combining accuracy scores and date column into one dataframe
    accscores = pd.concat([dateranges,maescores,R2scores,pears_c,p_values],axis=1,sort=False)  
   
    return accscores

#run regression on time frame of choice
roll_cg_13_weeks = RollingOLS(X_weekly,y_weekly,window=13)

