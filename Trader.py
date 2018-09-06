from FinancialExpert import FinancialExpert
from Networker import Networker
import os
import time


class Trader(FinancialExpert):
	def __init__(self, strategy=None):
		PUBLIC_KEY = os.environ.get("PUBLIC_KEY", default=None)
		SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
		self.fee = 0.075
		self.symbols = ["ADA", "BCC", "BNB", "BTC", "EOS", "ETC", "ETH", "ICX", "IOTA", "LTC", "NEO", "NULS", "ONT",
						"QTUM", "TRX", "XLM", "XRP", "VET"]

		self.networker = Networker(secret_key=SECRET_KEY,
								   public_key=PUBLIC_KEY)

		self.strategy = strategy
		if self.strategy is None:
			self.strategy = "DEFAULT"

		self.run()

		return

	def run(self):
		if self.strategy == "SUNRISE":
			return self.start_sunray_trading()
		elif self.strategy == "DEFAULT" or self.strategy == "SAFE":
			return

	def wait(self, seconds):
		time.sleep(seconds)
		return

	def start_sunray_trading(self):
		trading = True
		market_data = self.networker.get_market_data()
		lot_size_dict = self.networker.build_lot_size_dict(market_data=market_data)
		side = "BUY"
		while trading:
			# Step 1: Check available balance in USDT:
			account_info = self.networker.get_account_information()
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
				cs_data_averages = self.networker.get_cs_data_averages(cs_data=cs_data)
				decision = self.sunrays_based_descison(cs_data_averages=cs_data_averages,
												  forward_sensitivity=forward_sensitivity,
												  side=side,
												  max_dev=max_dev,  # TODO update max_dev every 10 minutes?
												  safety_factor=safety_factor)
				if not decision:
					wait(seconds=60)
					mins_passed += 1
					cs_data = self.networker.get_candlestick_data(symbol=chosen_currency_info['chosen_currency'], interval="1m",
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
							self.networker.get_latest_price(symbol=chosen_currency_info['chosen_currency'])['price'])

					order_amount = self.modify_amount_to_lot_size(amount_float=order_amount, lot_size=lot_size_dict[
						chosen_currency_info['chosen_currency']])

					order_data = self.networker.place_order(symbol=chosen_currency_info['chosen_currency'],
											 side=side,
											 o_type="MARKET",
											 quantity=order_amount)

					print(order_data)
					wait(
						seconds=30)  # Just to make sure order went through TODO remove naiveness from the absence of error handlings

					account_info = self.networker.get_account_information()
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
