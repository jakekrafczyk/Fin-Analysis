
# --- REQUESTING DATA FROM THE KRAKEN PUBLIC API TO USE FOR TRADING STRATEGIES AND CHART ANALYSES ---

import requests, json
import pandas as pd

#test response request
response = requests.get('https://api.kraken.com/0/public/Time')
status_code = response.status_code
content = response.content


# -- DAILY OHLCV DATA COLLECTION --

#kraken API only allows the last 72 data points to be collected, ie 72 days, 72 hours, etc
#set parameters for request and send request
params = {'pair': 'xbtusd', 'interval':1440,'since': 1483275600}		#interval is in minutes: 1440 = 60x24
p_response = requests.get('https://api.kraken.com/0/public/OHLC',params=params)
status_code = p_response.status_code

#convert data format from json to python
json_data = p_response.json()
OHLCV = json_data['result']['XXBTZUSD']

#convert date to a readable format
from datetime import datetime

for row in OHLCV:
	date = datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d')
	row[0] = date

	#calculate USD volume from vwap and BTC volume
	row[5] =  str(float(row[5]) * float(row[6]))	

OHLCV = pd.DataFrame(OHLCV)

OHLCV.columns = ['Date','Open','High','Low','Close','Volume USD','Volume BTC','Count']	

#drop the columns we dont need
OHLCV = OHLCV.drop(columns=['Count','Volume BTC'])

#drop rows we dont need
for i, row in OHLCV.iterrows():
	if float(row[4]) == float(row[3]) == float(row[2]) == float(row[1]):
		OHLCV = OHLCV.drop([i]).reset_index(drop=True)


#rename and check dataset
dataset = OHLCV


# -- HOURLY OHLCV DATA COLLECTION --

#next we get the same data, but for the HOURLY
h_params = {'pair': 'xbtusd', 'interval':60,'since': 1483275600}
h_response = requests.get('https://api.kraken.com/0/public/OHLC',params=h_params)
h_status_code = h_response.status_code

#convert data format from json to python
h_json_data = h_response.json()
h_OHLCV = h_json_data['result']['XXBTZUSD']

#convert date to a readable format
for row in h_OHLCV:
	date = datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S')	#need to add %H:%M:%S for the hourly
	row[0] = date

	#calculate USD volume from vwap and BTC volume
	row[5] =  str(float(row[5]) * float(row[6]))

#turn into dataframe and add column headings
h_OHLCV = pd.DataFrame(h_OHLCV)
h_OHLCV.columns = ['Date','Open','High','Low','Close','Volume USD','Volume BTC','Count']	

#drop the columns we dont need
h_OHLCV = h_OHLCV.drop(columns=['Count','Volume BTC'])

#drop the rows we dont need
for i, row in h_OHLCV.iterrows():
	if float(row[4]) == float(row[3]) == float(row[2]) == float(row[1]):
		h_OHLCV = h_OHLCV.drop([i]).reset_index(drop=True)

h_dataset = h_OHLCV


