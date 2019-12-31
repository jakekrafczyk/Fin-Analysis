
# ---- PREPPING DATA FROM THE KRAKEN API AND TRANSFORMING IT INTO A CANDLESTICK 
#      CHART WITH VOLUME BY PRICE DISPLAYED ON THE HORIZONTAL AXIS ----

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.dates import num2date, date2num, DateFormatter
import datetime
from mpl_finance import candlestick_ohlc
import pandas as pd
from numpy import arange
import math
from kraken_req import dataset, h_dataset #Can import directly from the API request file
#from strat1 import dataset, ema21
# -- OR can import from strategy file with added buy/sell columns --

#print dataset.head to check if data imported correctly
print(dataset.head())

OHLC = dataset

#reformat dates into datetime and prices into floats
OHLC['Date'] = pd.to_datetime(OHLC['Date'])
OHLC['Date'] = [mdates.date2num(d) for d in OHLC['Date']]
OHLC['Open'] = OHLC['Open'].astype(float)
OHLC['High'] = OHLC['High'].astype(float)
OHLC['Low'] = OHLC['Low'].astype(float)
OHLC['Close'] = OHLC['Close'].astype(float)	 
OHLC['Volume USD'] = OHLC['Volume USD'].astype(float)  

# Re-arrange data so that theres a tuple for each day- required format for candlestick_ohlc function
quotes = [tuple(x) for x in OHLC[['Date','Open','High','Low','Close']].values]

# -- CREATING VOLUME BY PRICE HISTOGRAM -- 

#first we need to round all the closing values within the set interval
def custom_round(x, base=500):
    return int(base * math.trunc(float(x)/base))

#create function to group volume into different ranges
def round_and_group(df, base=500):
    # https://stackoverflow.com/questions/40372030/pandas-round-to-the-nearest-n
    df = df[['Close', 'Volume USD']].astype(float).copy()

    # Round to nearest interval
    df['Close'] = df['Close'].apply(lambda x: custom_round(x, base=base))

    #readying the function to set the minimum interval value, 1000000 is a filler value
    minclose = 1000000
    for x in df['Close']:
    	if x < minclose:
    		minclose = x

    #readying the function to set the maximum interval value, 1000 is a filler value
    maxclose = 1000
    for x in df['Close']:
    	if x > maxclose:
    		maxclose = x

    #fill in intervals where there isnt any volume data
    for i in range(minclose - base, maxclose + (base * 2), base):
    	if i not in df['Close']:
    		df = df.append({'Close' : i}, ignore_index=True)

    # Remove the date index
    df = df.set_index('Close')
    df = df.groupby(['Close']).sum()
    return df

#apply function to dataset with a chosen interval
bar_data = round_and_group(OHLC, base=250)	#<-- ADJUST VOLUME INTERVALS HERE

#print the grouped ranges with their corresponding volume(eg with base=500,
#a close value of 1500 infers the corresponding volume is within the range 1500-2000)
print(bar_data)	

# Prepare y axis data for the barchart
y_pos = arange(len(bar_data.index.values))

#define funcformatter function that converts volume values like 10,000 to 10k to reduce the label size
# % starts the value placeholder and f ends it. The value is defined to the right starting with %
def millions(x, pos):
    #The two args are the volume value and tick position
    return '%1.0fM' % (x*1e-6)


# -- CREATE A FUNCTION THAT RETURNS A CANDLESTICK PLOT WITH VOLUME BY PRICE 
#    SHOWN AS A BARH CHART ON THE SAME AXIS --

def create_plot(barh_x, barh_y, y_tick_labels, ohlc: tuple, title: str):
    # Example horizontal bar chart code taken from:
    # https://matplotlib.org/gallery/lines_bars_and_markers/barh.html
 	
    #creating the subplots
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)

    #width = 0.7 for DAILY, and 0.1 for HOURLY
    candlestick_ohlc(ax, ohlc, width=0.7,colorup='g', colordown='r');
    
    # - HERE IS WHERE STRATEGY BUY AND SELL MARKERS CAN BE ADDED IN - 
    #DEFINE ELSEWHERE BY ADDING A BOOLEAN FILLED 'BUY' COLUMN TO THE MAIN DATASET
    #plt.plot(OHLC.Date,OHLC.Close,linestyle='None', label = '')
    #plt.plot(OHLC[OHLC.Buy==True].Date,OHLC[OHLC.Buy==True].Close, '^k', label='Buy')
    #plt.plot(OHLC[OHLC.Sell==True].Date,OHLC[OHLC.Sell==True].Close, '^k', label='Sell', color = 'Pink')

    #set y lim for the y ticks
    plt.ylim(y_tick_labels[0],y_tick_labels[-1])

    #setting the ytick values
    ax.set_yticks(y_tick_labels)

    #set the xtick date values
    #NEEDS EDITING FOR DIFFERENT TIME FRAMES
    # VVV THIS IS FOR DAILY DATA
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
    # VVV THIS IS FOR HOURLY DATA
    #ax.xaxis.set_major_locator(mdates.HourLocator(interval=24))

    #add a grid
    plt.grid(True, axis='y')

    #plot emas or smas
    #plt.plot(OHLC['Date'], ema14, color = 'orange',label='14 Day EMA')
    #plt.plot(OHLC['Date'], ema18wk, color = 'c',label='18-wk EMA')
    #plt.legend(loc='upper right')

    #calculate pct change
    pct_change = OHLC['Close'].pct_change()

    #add pct change to dataset
    OHLC['% Change'] = pct_change
    
    #add twin axes in to overlap the candlestick chart axis with the barh chart axis
    ax2 = ax.twinx().twiny()
  
    #create horizontal barchart
    ax2.barh(barh_y, barh_x, height=.9, align='edge', color='Blue')

    #erase facecolor so both charts are visible
    ax.set_facecolor("none")

    #set the positioning of the figure
    ax2.set_position(matplotlib.transforms.Bbox([[0.07,0.12],[0.95,0.9]]))

    #format the right y-axis
    formatter = mticker.LinearLocator(len(y_tick_labels))
    ax2.yaxis.set_major_locator(formatter)

    #establish same y limits for the second y axis
    plt.ylim(0,len(y_tick_labels)-1)

    #format the ticks for the top x axis
    xt = ax.get_xticks()
    new_xticks = [datetime.date.isoformat(num2date(d)) for d in xt]
    ax.set_xticklabels(new_xticks,rotation=45, horizontalalignment='right')
    formatter = mticker.FuncFormatter(millions)	#millions is a user defined function
    ax2.xaxis.set_major_formatter(formatter)
  
    #padding the top axis labels to avoid overlap with the title
    ax2.tick_params(axis='x', pad=10)

    #setting bottom axis labels
    ax.set_xlabel('Dates')
    ax.set_title(title)
    plt.xticks(rotation=325)

    #bring the candlestick chart on top of the barchart
    ax = ax.set_zorder(2)
    ax2 = ax2.set_zorder(1)

    plt.show()


# -- RUN THE FUNCTION WITH CHOSEN PARAMETERS --
vbp_plot = create_plot(bar_data['Volume USD'], y_pos, bar_data.index.values, 
	quotes, 'BTC/USD Volume By Price')




