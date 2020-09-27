import websocket, config, json, talib, numpy
import pandas as pd
from time import sleep
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

futures_websocket = 'wss://fstream3.binance.com/ws/btcusdt@kline_1m'

client = Client(config.API_KEY, config.API_SECRET)

TRADE_SYMBOL = 'BTCUSDT'
SYMBOL_POS = 41
TRADE_QUANTITY = 10 #sample quantity

EMA1_PERIOD = 6
EMA2_PERIOD = 20

closes = []

def on_open(ws):
    print('connecting..')

def on_close(ws):
    print('connection closed')

def on_message(ws, message):
    global closes

    json_msg = json.loads(message)
    candle = json_msg['k']
    candle_closed = candle['x']
    close = candle['c']

    if candle_closed:
        print('Candle closed at: {}'.format(close))
        closes.append(float(close))
        last_close = closes[-1]
        print('Closes:')
        print(closes)

        #Trading Strategy
        if len(closes) > EMA1_PERIOD:
            np_closes = numpy.array(closes)
            EMA1 = talib.EMA(np_closes, EMA1_PERIOD)
            last_EMA1 = EMA1[-1]
            print('Current EMA1 is: {}'.format(last_EMA1))

        if len(closes) > EMA2_PERIOD:
            np_closes = numpy.array(closes)
            EMA2 = talib.EMA(np_closes, EMA2_PERIOD)
            last_EMA2 = EMA2[-1]
            print('Current EMA2 is: {}'.format(last_EMA2))

            #Buy Long
            if last_close > last_EMA1 and last_EMA1 > last_EMA2:
                check_if_in_position = client.futures_position_information()
                df = pd.DataFrame(check_if_in_position)
                position_amount = df.loc[SYMBOL_POS, 'positionAmt']
                
                if float(position_amount) == 0:
                    print('EMAs crossed to the upside, executing buy order!')

                    try:
                        order = client.futures_create_order(symbol=TRADE_SYMBOL, side='BUY', type='MARKET', quantity=TRADE_QUANTITY)

                        sleep(2)
                    
                    except BinanceAPIException as e:
                        #error handling here
                        print(e)
                    except BinanceOrderException as e:
                        #error handling here
                        print(e)
                
                else:
                    print('Buy signal is on but you are already in position.')
            
            #Take Profit or Loss (for long position)
            if last_EMA1 < last_EMA2:
                check_if_in_position = client.futures_position_information()
                df = pd.DataFrame(check_if_in_position)
                position_amount = df.loc[SYMBOL_POS, 'positionAmt']

                sleep(2)

                check_side = client.futures_account_trades()
                df = pd.DataFrame(check_side)
                check_side = df['side'].iloc[-1]

                if float(position_amount) == 0:
                    print('Nothing to liquidate, you do not own any position.')
                elif check_side == 'SELL':
                    print('You are shorting the market.')
                else:
                    print('Selling your position')

                    try:
                        order = client.futures_create_order(symbol=TRADE_SYMBOL, side='SELL', type='MARKET', quantity=TRADE_QUANTITY)

                        sleep(2)

                    except BinanceAPIException as e:
                        #error handling here
                        print(e)
                    except BinanceOrderException as e:
                        #error handling here
                        print(e)
            
            #Sell Short
            if last_close < last_EMA1 and last_EMA1 < last_EMA2:
                check_if_in_position = client.futures_position_information()
                df = pd.DataFrame(check_if_in_position)
                position_amount = df.loc[SYMBOL_POS, 'positionAmt']
                
                if float(position_amount) == 0:
                    print('EMAs crossed to the downside, executing sell order!')

                    try:
                        order = client.futures_create_order(symbol=TRADE_SYMBOL, side='SELL', type='MARKET', quantity=TRADE_QUANTITY)

                        sleep(2)

                    except BinanceAPIException as e:
                        #error handling here
                        print(e)
                    except BinanceOrderException as e:
                        #error handling here
                        print(e)
                    
                else:
                    print('Sell signal is on but you are already in position.')
            

            #Take Profit or Loss (for short position)
            if last_close > last_EMA2:
                check_if_in_position = client.futures_position_information()
                df = pd.DataFrame(check_if_in_position)
                position_amount = df.loc[SYMBOL_POS, 'positionAmt']

                check_side = client.futures_account_trades()
                df = pd.DataFrame(check_side)
                check_side = df['side'].iloc[-1]

                if float(position_amount) == 0:
                    print('Nothing to liquidate, you do not own any position.')
                elif check_side == 'BUY':
                    print('You are long in the market.')
                else:
                    print('Liquidating your position.')
                    try:
                        order = client.futures_create_order(symbol=TRADE_SYMBOL, side='BUY', type='MARKET', quantity=TRADE_QUANTITY)

                        sleep(2)

                    except BinanceAPIException as e:
                        #error handling here
                        print(e)
                    except BinanceOrderException as e:
                        #error handling here
                        print(e)

ws = websocket.WebSocketApp(futures_websocket, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()









