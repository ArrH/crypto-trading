from FinancialExpert import FinancialExpert
from BinanceAPI import BinanceAPI
import os
import time
import concurrent.futures


class Trader(FinancialExpert):
	def __init__(self, strategy=None):
		PUBLIC_KEY = os.environ.get("PUBLIC_KEY", default=None)
		SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
		self.profit_seek = 0.005
		self.risk_aversion = 1
		self.fee = 0.00075
		self.profit_seek = ((1+self.profit_seek) / ((1-self.fee)**2) ) - 1
		self.position_spread = 5
		self.base_currency = "USDT"
		self.symbols = ["ADA", "BNB", "BTC", "BTT", "CELR", "EOS", "ETC", "ETH", "FET", "HOT", "ICX",
						"IOST", "IOTA", "LTC", "NEO", "ONT", "PAX", "QTUM", "TRX", "XLM", "XRP", "VET", "ZIL"]

		self.binanceAPI = BinanceAPI(secret_key=SECRET_KEY,
								   public_key=PUBLIC_KEY)

		print("Initializing the Trader")
		print("Profit_seek:", self.profit_seek*100, "% per trade")
		print("Risk aversion:", self.risk_aversion)
		print("----")

		print("Base currency:", self.base_currency)

		print("Currency list:")
		print(self.symbols)
		print("----")

		print("Assumed fee percentage:")
		print(self.fee*100, "%")
		print("----")

		print("Position spread: ", self.position_spread)
		print("----")

		self.set_strategy()

		r = self.binanceAPI.get_ping()

		self.market_data = self.binanceAPI.get_market_data()
		print("Market Data Acquired")
		print("----")

		self.lot_size_dict = self.binanceAPI.build_lot_size_dict(market_data=self.market_data)
		print("lot size dictionary initiliazed:")
		print(self.lot_size_dict)
		print("----")

		print("Trader Initialized. Starting Trading...")
		print("----")

		self.run()

		return

	def set_strategy(self, strategy=None):
		if strategy is None:
			self.strategy = "SIMPLE_STRATEGY"
			print("Trading strategy chosen: ", self.strategy)
			print("----")
		else:
			print("not implemented")

	def run(self):
		if self.strategy == "SIMPLE_STRATEGY":
			self.simple_strategy_trading()

	def wait(self, seconds):
		time.sleep(seconds)
		return


	def simple_strategy_trading(self):
		# Step 1: Get usdt balance and decide upon the purchase amounts in USDT
		balance_usdt = self.get_usdt_balance()
		# balance_usdt = 11
		# self.bid_size_usdt = balance_usdt/self.position_spread
		self.bid_size_usdt = 11

		# Enter the trading loop
		trading = True
		symbols = self.symbols
		symbols_in_bid = []

		start_time = time.time()

		while trading:

			if balance_usdt > 10:

				# Step 2: Choose currency to bid on
				bid_currency = self.choose_bid_currency(symbols=symbols)

				if bid_currency is not None:

					# Step 3: Place a bid
					combined_symbol = bid_currency + self.base_currency
					order_placed = self.place_bid(self.bid_size_usdt, symbol=combined_symbol)
					if order_placed == True:
						symbols.remove(bid_currency)
						symbols_in_bid.append(bid_currency)


						print("positions taken:")
						print(symbols_in_bid)
						print("----")

			balance_usdt = self.get_usdt_balance()
			if time.time() - start_time > 3600:
				start_time = time.time()
				symbols = self.symbols

			print("Balance USDT: ", balance_usdt)
			print("----")
			time.sleep(60)

		return


	def get_usdt_balance(self):
		account_info = self.binanceAPI.get_account_information()
		# print(account_info)
		free_balance_usdt = float(self.check_free_balances_for_currency_list(account_info=account_info,
																			 currency_list=['USDT'])['USDT'])
		return free_balance_usdt

	def choose_bid_currency(self, symbols):
		# Iterate through all the symbols
		for symbol in self.symbols:

			# Get information about the currency
			combined_symbol = symbol+self.base_currency
			symbol_candlestick_data = self.binanceAPI.get_candlestick_data(symbol=combined_symbol, interval="5m", limit="60")

			# Check if it makes sense to bid on the currency
			worth_bidding_on = self.decide_whether_to_bid(combined_symbol=combined_symbol, symbol_candlestick_data=symbol_candlestick_data)
			if worth_bidding_on == True:
				print("Worthwhile currency found. Bidding on: ", combined_symbol)
				print("----")
				return symbol
			else:
				continue

	def decide_whether_to_bid(self, combined_symbol, symbol_candlestick_data):
		# Step 1: Get hourly min and max
		per_min = 10000000000.
		per_max = 0.
		for i in range(len(symbol_candlestick_data)):
			current = float(symbol_candlestick_data[i][4])
			per_max = max([per_max, current])
			per_min = min([per_min, current])

		# Step 2: Get current price
		current_price = float(self.binanceAPI.get_latest_price(symbol=combined_symbol)['price'])

		# Step 3: TODO identify trend and riskiness of the investment

		# Step 4: Make decision
		decision = False
		if current_price < (per_max+per_min)/2 \
				and current_price > per_min \
				and per_max/current_price > 1+self.profit_seek: #IMPORTANT
			decision = True

		return decision

	def place_bid(self, usdt_amount, symbol):
		# make an exchange to currency of choice
		order_placed = False
		order_amount = float(usdt_amount) / float(self.binanceAPI.get_latest_price(symbol=symbol)['price'])
		order_amount = self.modify_amount_to_lot_size(amount_float=order_amount, lot_size=self.lot_size_dict[
			symbol])
		order_data = self.binanceAPI.place_order(symbol=symbol,
												 side="BUY",
												 o_type="MARKET",
												 quantity=order_amount)
		purchase_fills = {}
		try:
			for fill in order_data['fills']:
				purchase_fills['price'] += float(fill['price'])
				purchase_fills['qty'] += float(fill['qty'])
			order_placed = True
		except:
			print(order_data)
			print(order_amount)
			print(symbol, " order did not went through. Aborting operation and moving to a new bid...")
			order_placed = False

		if order_placed == True:
			purchase_price = float(purchase_fills['price'])
			purchase_quantity = float(purchase_fills['qty'])

			print("Bought ", purchase_quantity, "of ", symbol)
			print(order_data)

			# Place Take Profit order
			take_profit_price = round(purchase_price * (1+self.profit_seek), len( str(purchase_price).split(".", 1)[1] ) )
			# take_profit_price = self.modify_amount_to_lot_size(amount_float=take_profit_price, lot_size=self.lot_size_dict[symbol])

			print(take_profit_price)
			print(purchase_price)

			take_profit_order = self.binanceAPI.place_limit_order(symbol=symbol,
																  side="SELL",
																  stop_price=take_profit_price,
																  quantity=purchase_quantity)

			# TODO If take profit is not successful, handle that somehow.
			# TODO Start a parallel process that dynamically check for potential market crashes, in other words, tries to avoid losses.


			print("Limit order placed:")
			print(take_profit_order)
			print("----")

		return order_placed

	# def update_symbols_in_bid(self, symbols_in_bid):
	# 	for symbol in symbols_in_bid:
	# 		symbol_balance = float(self.check_free_balances_for_currency_list(account_info=account_info,
	# 																		 currency_list=['USDT'])['USDT'])












	def start_safe_trading(self):
		"""
		safe trading strategy description
		:return:
		"""

		# Analyze all the currencies in parallel. If found one which is cool to be purchased - break the loop and continue
		currency_found = False
		chosen_currency = ""
		while currency_found is False:
			currency_decisions ={}
			with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.symbols)) as executor:
				# Start the load operations and mark each future with its URL
				future_to_symbol = {executor.submit(self.make_decision_sunray, symbol): symbol for symbol in self.symbols}
				for future in concurrent.futures.as_completed(future_to_symbol):
					symbol = future_to_symbol[future]
					try:
						data = future.result()
					except Exception as exc:
						print('%r generated an exception: %s' % (symbol, exc))
					else:
						currency_decisions[symbol] = data

			for currency, decision in currency_decisions.items():
				if decision is True:
					chosen_currency = currency
					currency_found = True
					break
				else:
					continue

		# Get last 2 candle stick data points and place an order to purchase the currency for maximum of an average of
		# the previous
		combined_symbol = chosen_currency + "USDT"
		cs_data = self.binanceAPI.get_candlestick_data(symbol=combined_symbol, interval="1m",
													  limit=2)
		cs_data_averages = self.get_cs_data_averages(cs_data=cs_data)
		purchase_price = cs_data_averages[0]
		
		order_data = self.binanceAPI.place_take_profit_order() # TODO +  handle errors

		# Send calls to check if the order went through

		# Once the order for sale is through, place an order to sell at the desired price. Also, place a stop_limit order
		# that prevents from loss



	def start_sunray_trading(self):
		trading = True
		market_data = self.binanceAPI.get_market_data()
		lot_size_dict = self.binanceAPI.build_lot_size_dict(market_data=market_data)
		side = "BUY"
		while trading:
			# Step 1: Check available balance in USDT:
			account_info = self.binanceAPI.get_account_information()
			print(account_info)
			free_balance_usdt = float(self.check_free_balances_for_currency_list(account_info=account_info,
																			currency_list=['USDT'])['USDT']) * 0.99
			print("Amount of free USDT in your account: ", free_balance_usdt)

			# Step 2: Choose currency and get associated data
			# TODO implement a way to determine if we are looking tops or bottoms in the market (based on the amount of USDT)
			print("Selecting currency for trading... ~ 60seconds ")
			chosen_currency_info = self.choose_currency_for_trading()
			print("Currency for trading has been chosen: ", chosen_currency_info['chosen_currency'])
			cs_data = chosen_currency_info["cs_data"]
			max_dev = chosen_currency_info['max'] - chosen_currency_info['min']
			chosen_currency_lefthand = chosen_currency_info['chosen_currency'][:-4]
			free_balance_crypto = self.check_free_balances_for_currency_list(account_info=account_info,
																		currency_list=[chosen_currency_lefthand])[
				chosen_currency_lefthand]

			safety_factor = 0.4
			forward_sensitivity = 2  # Isn't this a bit of a big? TEST

			data_amount = 15 + forward_sensitivity  # 15 is an arbitrary number TODO
			running = True

			print("Starting the Sunrays algorithm")
			print("Action: ", side)
			mins_passed = 0
			while running:

				# Step 3: check if it makes sense to purchase
				cs_data_averages = self.get_cs_data_averages(cs_data=cs_data)
				decision = self.sunrays_based_descison(cs_data_averages=cs_data_averages,
												  forward_sensitivity=forward_sensitivity,
												  side=side,
												  max_dev=max_dev,  # TODO update max_dev every 10 minutes?
												  safety_factor=safety_factor)
				if not decision:
					self.wait(seconds=60)
					mins_passed += 1
					cs_data = self.binanceAPI.get_candlestick_data(symbol=chosen_currency_info['chosen_currency'], interval="1m",
												   limit=str(data_amount))
					if mins_passed >= 20 and side == "BUY":
						print(
							"Seems like this currency is not fluctuating enough at this moment... Let's choose another one. ")
						print("--->")
						running = False
				else:
					print("Placing an order: ", side)
					# Place order
					if side == "SELL":
						order_amount = float(free_balance_crypto)
						if order_amount == 0.0:
							free_balance_crypto = self.check_free_balances_for_currency_list(account_info=account_info,
																						currency_list=[
																							chosen_currency_lefthand])[
								chosen_currency_lefthand]
							order_amount = float(free_balance_crypto)
					elif side == "BUY":
						order_amount = float(free_balance_usdt)
						order_amount = order_amount / float(
							self.binanceAPI.get_latest_price(symbol=chosen_currency_info['chosen_currency'])['price'])

					order_amount = self.modify_amount_to_lot_size(amount_float=order_amount, lot_size=lot_size_dict[
						chosen_currency_info['chosen_currency']])

					order_data = self.binanceAPI.place_order(symbol=chosen_currency_info['chosen_currency'],
											 side=side,
											 o_type="MARKET",
											 quantity=order_amount)

					print(order_data)
					self.wait(seconds=30)  # Just to make sure order went through
					# TODO remove naiveness from the absence of error handlings

					account_info = self.binanceAPI.get_account_information()
					if side == "SELL":
						side = "BUY"
						free_balance_usdt = self.check_free_balances_for_currency_list(account_info=account_info,
																				  currency_list=['USDT'])['USDT']
						running = False
					elif side == "BUY":
						side = "SELL"
						free_balance_crypto = self.check_free_balances_for_currency_list(account_info=account_info,
																					currency_list=[
																						chosen_currency_lefthand])[
							chosen_currency_lefthand]
						print("Amount in crypto now in your acc: ", free_balance_crypto)


