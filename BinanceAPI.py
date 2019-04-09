import time
import hashlib
import hmac
import requests
from urllib.parse import urlencode
import json

class BinanceAPI():
	"""
	This is a class that is used to communicate with the Binance API. It also contains a few methods that process the returned
	data in a format used by the Trader.
	"""
	def __init__(self, public_key, secret_key):
		self.public_key = public_key
		self.secret_key = secret_key
		print("Binance API Initialized")
		print("----")
		return

	def make_public_request(self, endpoint, query_params=None):
		"""
		makes a public request
		:param endpoint: endpoint which will be called
		:param query_params: self explanatory :)
		:return: dict of the request results
		"""
		# TODO error handling
		request_url = self.build_request_url(endpoint=endpoint, query_params=query_params)
		try:
			r = requests.get(url=request_url)
			print("Request Successfully made, status ", r.status_code)
			print("type: public")
			print("url: ", request_url)
			print("----")
			return json.loads(r.text)
		except:
			print("The following request has failed:")
			print("type: public")
			print("url: ", request_url)
			return "{}"


	def make_private_request(self, method, endpoint, query_params=None):
		"""
		Makes a private request
		:param method: GET or POST
		:param endpoint: endpoint which will be called
		:param query_params: self explanatory :)
		:return: dict of the request results
		"""

		# TODO error handling

		# Build the basic required params dict and put it into url encode
		if query_params is None:
			query_params = {}
		query_params["timestamp"] =self. get_time_in_ms()
		params = urlencode(query_params)

		# Creat the signature
		hashedsig = hmac.new(self.secret_key.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()

		headers = {"X-MBX-APIKEY": self.public_key}

		request_url = self.build_endpoint_url(endpoint=endpoint) + "?" + params + "&signature={hashedsig}".format(
			hashedsig=hashedsig)
		# print(request_url)
		if method == "POST":
			r = requests.post(url=request_url, headers=headers)
		else:
			r = requests.get(url=request_url, headers=headers)
		return json.loads(r.text)

	def get_time_in_ms(self):
		"""
		returns current time in ms
		:return: int time in ms
		"""
		return int(time.time() * 1000)

	def build_query_params_string(self, query_params):
		query_params_string = ""
		for key, value in query_params.items():
			query_params_string += "{key}={value}&".format(key=key, value=value)
		return query_params_string[:-1]

	def build_endpoint_url(self, endpoint):
		return "https://api.binance.com{endpoint}".format(endpoint=endpoint)

	def build_request_url(self, endpoint, query_params=None):
		request_url = self.build_endpoint_url(endpoint=endpoint)
		if query_params is not None:
			request_url += "?" + self.build_query_params_string(query_params)
		return request_url

	def build_lot_size_dict(self, market_data):
		"""
		builds a dict that has currency shorthand as keys and respective lot size as
		:param market_data: markert data as retunred by the market data endpoint
		:return:
		"""
		return_dict = {}
		for currency in market_data['symbols']:
			for filter_type in currency["filters"]:
				if filter_type["filterType"] == "LOT_SIZE":
					step_size = filter_type["stepSize"]
					lot_size = 0
					for char in step_size:
						if char == "0":
							lot_size += 1
						if char == "1":
							break
			return_dict[currency["symbol"]] = lot_size
		return return_dict

	def build_precision_dict(self, market_data):
		"""
		builds a dict that has currency shorthand as keys and respective lot size as
		:param market_data: markert data as retunred by the market data endpoint
		:return:
		"""
		return_dict = {}
		for currency in market_data['symbols']:
			return_dict[currency["symbol"]] = currency['quotePrecision']
		return return_dict

	def get_ping(self):
		return self.make_public_request(endpoint="/api/v1/ping")

	def get_server_time(self):
		return self.make_public_request(endpoint="/api/v1/time")

	def get_market_data(self):
		return self.make_public_request(endpoint="/api/v1/exchangeInfo")

	def get_market_depth(self, symbol, limit=None):
		query_params = {"symbol": symbol,
					  	"limit": limit}
		return self.make_public_request(endpoint="/api/v1/depth", query_params=query_params)

	def get_recent_trades(self, symbol, limit=None):
		query_params = {"symbol": symbol,
					  	"limit": limit}
		return self.make_public_request(endpoint="/api/v1/trades", query_params=query_params)

	def get_old_trades(self, symbol, limit=None, fromId=None):
		query_params = {"symbol": symbol,
					  	"limit": limit,
						"fromId": fromId}
		return self.make_public_request(endpoint="/api/v1/historicalTrades", query_params=query_params)

	def get_agr_trades(self, symbol, limit=None, fromId=None):
		query_params = {"symbol": symbol,
					  	"limit": limit,
						"fromId": fromId}
		return self.make_public_request(endpoint="/api/v1/historicalTrades", query_params=query_params)


	def get_account_information(self):
		return self.make_private_request(method="GET", endpoint="/api/v3/account")

	def place_order(self, symbol, side, o_type, quantity):
		order_info = {"symbol": symbol,
					  "side": side,
					  "type": o_type,
					  "quantity": quantity}
		return self.make_private_request(method="POST", endpoint="/api/v3/order", query_params=order_info)

	def place_stop_loss_order(self, symbol, side, stop_price, quantity):
		order_info = {"symbol": symbol,
					  "side": side,
					  "type": "STOP_LOSS",
					  "quantity": quantity,
					  "stopPrice": stop_price
					  }
		return self.make_private_request(method="POST", endpoint="/api/v3/order", query_params=order_info)

	def place_limit_order(self, symbol, side, stop_price, quantity):
		order_info = {"symbol": symbol,
					  "side": side,
					  "type": "LIMIT",
					  "quantity": quantity,
					  "price": stop_price,
					  "timeInForce": "GTC"
					  }
		return self.make_private_request(method="POST", endpoint="/api/v3/order", query_params=order_info)

	def place_take_profit_order(self, symbol, side, stop_price, quantity):
		order_info = {"symbol": symbol,
					  "side": side,
					  "type": "TAKE_PROFIT",
					  "quantity": quantity,
					  "stopPrice": stop_price
					  }
		return self.make_private_request(method="POST", endpoint="/api/v3/order", query_params=order_info)



	def place_test_order(self, symbol, side, o_type, quantity):
		order_info = {"symbol": symbol,
					  "side": side,
					  "type": o_type,
					  "quantity": quantity}
		return self.make_private_request(method="POST", endpoint="/api/v3/order/test", query_params=order_info)

	def get_candlestick_data(self, symbol, interval, limit):
		query_params = {"symbol": symbol,
						"interval": interval,
						"limit": limit}
		if query_params["symbol"] is not None:
			return self.make_public_request(endpoint="/api/v1/klines", query_params=query_params)
		else:
			return "Forgot symbol. Abort"

	def get_latest_price(self, symbol):
		query_params = {"symbol": symbol}
		if query_params["symbol"] is not None:
			return self.make_public_request(endpoint="/api/v1/ticker/price", query_params=query_params)
		else:
			return "Forgot symbol. Abort"