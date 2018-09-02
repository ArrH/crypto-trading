from helpers import *
import json

def get_account_information():
	return make_private_request(method="GET", endpoint="/api/v3/account")
	
def place_order(symbol, side, o_type, quantity):
	order_info = {"symbol": symbol,
				  "side": side,
				  "type": o_type,
				  "quantity": quantity}
	return make_private_request(method="POST", endpoint="/api/v3/order", query_params=order_info)

def get_candlestick_data(symbol, interval, limit):
	query_params = {"symbol": symbol,
					"interval": interval,
					"limit": limit}
	if query_params["symbol"] is not None:
		return make_public_request(endpoint="/api/v1/klines", query_params=query_params)
	else:
		return "Forgot symbol. Abort"
		

def get_latest_price(symbol):
	query_params = {"symbol": symbol}
	if query_params["symbol"] is not None:
		return make_public_request(endpoint="/api/v1/ticker/price", query_params=query_params)
	else:
		return "Forgot symbol. Abort"
		
