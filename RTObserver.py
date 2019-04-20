from BinanceAPI import BinanceAPI
from threading import Thread
import time


class RTObserver(BinanceAPI):
	"""
	The primary functions of this class are:
	1. Observe the order data and update Trader accordingly.
	2. Observe marker data in order to prevent the stop loss.
	"""
	def __init__(self, public_key, secret_key, symbol, purchase_price, purchase_quantity, order_id, stop_loss_price):
		self.running = True
		self.run_interval = 60 # seconds

		self.public_key = public_key
		self.secret_key = secret_key
		self.symbol = symbol
		self.purchase_price = purchase_price
		self.purchase_quantity = purchase_quantity
		self.order_id = order_id
		self.stop_loss_price = stop_loss_price

		return

	def run(self):
		while self.running:
			# Check if the order is still open
			order_open = self.check_if_order_open()

			# if trade is still open, check for stop loss
			if order_open:
				stopped_loss = self.stop_loss()

			# self stop if order was filled or if the stop loss was executed
			if order_open == False or stopped_loss == True:
				self.stop()

			time.sleep(self.run_interval)

	def stop(self):
		self.running = False

	def check_if_order_open(self):
		order_data = self.get_order_data(symbol=self.symbol,
										 order_id=self.order_id)

		if order_data['status'] == "FILLED":
			return False
		else:
			return True

	def stop_loss(self):
		# Get the current price
		stop_loss_executed = False
		current_symbol_price = float(self.get_latest_price(symbol=self.symbol)['price'])

		# Check whether the current price is below or at the stop loss price
		if current_symbol_price <= self.stop_loss_price:
			# Cancel the open order - strict
			while not stop_loss_executed:
				cancel_request = self.cancel_order(symbol=self.symbol,
												   order_id=self.order_id)

				try:
					if cancel_request['status'] == "CANCELED":
						stop_loss_executed == True
				except:
					print("Cancel order failed, trying again")
					time.sleep(2) # 2 second wait #TODO is this a good number?


		return stop_loss_executed



class RTObserverRunner(Thread):
	def __init__(self, *args, **kwargs):
		super().__init__()
		self.target = RTObserver(*args, **kwargs)
		self.stop = self.target.stop
		self.run = self.target.run