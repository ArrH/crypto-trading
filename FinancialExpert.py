


class FinancialExpert():
	"""
	Financial Expert is a class that mainly contains various computations to process and or predict financial trends,
	prices, etc.
	This class does not contain strategy level algorithms. For those, the user is referred to the Trading.py
	"""
	def __init__(self):
		return

	def sunrays_based_descison(self, cs_data_averages, forward_sensitivity, side, max_dev, safety_factor):
		"""
		This function contains an algorithm that (tries) to predict the change in the price direction. For the details
		regarding the logic behind it, please refer to the README.md .
		:param cs_data_averages: List of the open/closing prices averages
		:param forward_sensitivity: How many prices at the end of the lsit should be of changed direction
		:param side: SELL or BUY
		:param max_dev: Maximum deviation between the prices during the timeframe (chosen by the user)
		:param safety_factor: Lower risk factor reduces the likelihood of getting into the pump/dump scams
		:return: True if algo think we should make the trade, False otherwise
		"""
		heights_list = []
		for i in range(1, forward_sensitivity + 2):
			heights_list.append(cs_data_averages[-i] - cs_data_averages[0])

		if side == "BUY":
			if heights_list[-1] < 0:
				decision = True
			else:
				return False

		elif side == "SELL":
			if heights_list[-1] > 0:
				decision = True
			else:
				return False

		if abs(heights_list[-1]) >= (safety_factor * max_dev):
			decision = True
		else:
			return False

		for i in range(forward_sensitivity):
			if abs(heights_list[i]) < abs(heights_list[i + 1]):
				decision = True
			else:
				return False

		return decision

	def choose_currency_for_trading(self):
		"""
		This function performs some analysis on the candlestick_data of each symbol
		:return: dict with a data about the currency we are going to trade
		"""
		versus_symbol = "USDT"
		max_change = 0
		stability_sc = 0
		chosen_currency = ""
		average = 0
		best_min, best_max = 0, 0
		chosen_cs_data = None
		for symbol in self.symbols:
			combined_symbol = symbol + versus_symbol
			cs_data = self.networker.get_candlestick_data(symbol=combined_symbol, interval="1m", limit="60")
			hist_an = self.cs_history_analysis(cs_data=cs_data)
			current_price = float(self.networker.get_latest_price(symbol=combined_symbol)['price'])
			rel_change = (hist_an['max'] / hist_an['min'] - 1) * 100
			stability_score = abs(current_price - hist_an['average']) / (hist_an['max'] - hist_an['min'])

			if (rel_change > max_change) and (stability_score < 0.5) and (current_price < hist_an['average']) and \
					(self.check_profitability(p2=hist_an['max'], p1=hist_an['min'], margin=4. / 1000) is True):
				max_change = rel_change
				chosen_currency = combined_symbol
				stability_sc = stability_score
				average = hist_an['average']
				best_min, best_max = hist_an['min'], hist_an['max']
				chosen_cs_data = cs_data

		if chosen_cs_data is not None:
			return {"chosen_currency": chosen_currency,
					"max_change": max_change,
					"stability_score": stability_sc,
					"average": average,
					"min": best_min,
					"max": best_max,
					"cs_data": chosen_cs_data[18:]
					}
		else:
			return None

	def compound_visualizer(self, your_sum, days, gain_after_sell, sales_per_day):
		"""
		Calculates how much profit you will make starting with the initial sum and with the supplied parameters.
		:param your_sum: starting sum
		:param days: how many days you will trade
		:param gain_after_sell: percentage you expect to make after each sale
		:param sales_per_day: how many sells you will make in a day
		:return: float number that is the profit
		"""
		for i in range(days):
			for k in range(sales_per_day):
				your_sum += your_sum * gain_after_sell
		print(your_sum - 100)

	def profit_calc(self, s1, p2, p1):
		"""
		calculates the profit after one sale, taking fee's into account
		:param s1: your sum
		:param p2: price at which sold
		:param p1: price at which bought
		:return: your sum after sale
		"""
		f = self.fee/ 100
		return s1 * (p2 / p1 * (1 - f) ** 2 - 1)

	def check_profitability(self, p2, p1, margin):
		"""
		check whether the trade would be profitable, taking fee's into account
		:param p2: sell price
		:param p1: buy price
		:param margin: what kind of profit in percents you want to make
		:return: True if profitable, False if not
		"""
		f = self.fee / 100
		margin = margin / 100 * 2 # Safety factor techniques borrowed straight from the civil engineers
		if p2 / p1 > (margin + 1) / ((1 - f) ** 2):
			return True
		else:
			return False

	def cs_history_analysis(self, cs_data):
		"""
		analyzes candlestick data and puts results into an easy to read format
		:param cs_data: candlestick data in a list
		:return: dict with results
		"""
		per_min = 10000000.
		per_max = 0.
		per_average = 0.
		for i in range(len(cs_data)):
			current = float(cs_data[i][4])
			per_max = max([per_max, current])
			per_min = min([per_min, current])
			per_average += current
		per_average = per_average / len(cs_data)
		return {"max": per_max, "min": per_min, "average": per_average}

	def get_cs_data_averages(self, cs_data):
		"""
		averages open/close prices for the cs_data
		:param cs_data: candlestick data in a list
		:return: list of averages in the same order as supplied with cs_data (timewise)
		"""
		cs_data_averages = []
		for i in range(len(cs_data)):
			cs_data_averages.append((float(cs_data[i][1]) + float(cs_data[i][4])) / 2)
		return cs_data_averages

	def modify_amount_to_lot_size(self, amount_float, lot_size):
		"""
		Makes sure the float does not have too many digits according to the lot size
		:param amount_float: amount
		:param lot_size: lot size
		:return: modified amount
		"""
		return_float = ""
		amount_float = str(amount_float)
		for char in amount_float:
			return_float += str(char)
			if char == ".":
				break
		for i in range(len(return_float), len(return_float) + lot_size):
			try:
				return_float += str(amount_float[i])
			except:
				break
		return float(return_float)

	def check_free_balances_for_currency_list(self, account_info, currency_list):
		free_balances = {}
		if account_info["canTrade"]:
			balances = account_info["balances"]
			for balance in balances:
				if balance["asset"] in currency_list:
					free_balances[balance["asset"]] = balance["free"]
		return free_balances