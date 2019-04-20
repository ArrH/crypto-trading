from FinancialExpert import FinancialExpert
from BinanceAPI import BinanceAPI
import os
import time
from RTObserver import RTObserverRunner


class Trader(FinancialExpert):
	def __init__(self, strategy=None):
		self.public_key = os.environ.get("PUBLIC_KEY", default=None)
		self.secret_key = os.environ.get("SECRET_KEY", default=None)
		self.profit_seek = 0.005
		self.risk_aversion = 20
		self.fee = 0.00075
		self.profit_seek = ((1+self.profit_seek) / ((1-self.fee)**2) ) - 1
		self.position_spread = 5
		self.base_currency = "USDT"
		self.symbols = ["ADA", "BNB", "BTC", "BTT", "CELR", "EOS", "ETC", "ETH", "FET", "HOT", "ICX",
						"IOST", "IOTA", "LTC", "NEO", "ONT", "PAX", "QTUM", "TRX", "XLM", "XRP", "VET", "ZIL"]

		self.binanceAPI = BinanceAPI(secret_key=self.secret_key,
								     public_key=self.public_key)

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

		# Step 3: Make decision
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
		purchase_fills = {'price': 0.0,
						  'qty': 0.0}
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

			# Place Take Profit order - strict
			take_profit_order_placed = False
			while not take_profit_order_placed:
				take_profit_price = round(purchase_price * (1+self.profit_seek), len( str(purchase_price).split(".", 1)[1] ) )
				take_profit_order = self.binanceAPI.place_limit_order(symbol=symbol,
																	  side="SELL",
																	  stop_price=take_profit_price,
																	  quantity=purchase_quantity)
				# Check if take profit order was successful
				try:
					if take_profit_order['status'] == "NEW":
						take_profit_order_placed = True
				except:
						time.sleep(5)  # TODO random number

			# Start a parallel process that monitors the order status and executes stop loss sale if needed
			rto = RTObserverRunner(symbol=symbol,
								   purchase_price=purchase_price,
								   purchase_quantity=purchase_quantity,
								   order_id=take_profit_order['orderId'],
								   stop_loss_price=(1-self.risk_aversion * self.profit_seek) * purchase_price,
								   public_key=self.public_key,
								   secret_key=self.secret_key)
			rto.start()

		return order_placed



