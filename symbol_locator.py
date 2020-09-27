import config, csv
import pandas as pd
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

csvfile = open('symbol_locator.csv', 'w', newline='') 
symbols_writer = csv.writer(csvfile)

symbols = client.futures_position_information()
df = pd.DataFrame(symbols)
df.drop(['positionAmt', 'entryPrice', 'markPrice', 'unRealizedProfit', 'marginType', 'isolatedMargin', 'isAutoAddMargin', 'positionSide', 'liquidationPrice', 'leverage', 'maxNotionalValue'], axis=1, inplace=True)
print(df)

df.to_csv("symbol_locator.csv", index=True, sep=' ')