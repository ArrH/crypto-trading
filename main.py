import json
from account import *

def choose_currency_for_trading():
	symbols = ["ADA", "BCC", "BNB", "BTC", "EOS", "ETC", "ETH", "ICX", "IOTA", "LTC", "NEO", "NULS", "ONT", "QTUM", "TRX", "VET", "XLM", "XRP"]
	versus_symbol = "USDT"
	max_change = 0
	stability_sc = 0
	chosen_currency = ""
	average = 0
	best_min, best_max = 0, 0
	chosen_cs_data = None
	return_dict = {}
	for symbol in symbols:
		combined_symbol = symbol + versus_symbol
		cs_data = get_candlestick_data(symbol=combined_symbol, interval="1m", limit="60")
		hist_an = cs_history_analysis(cs_data=cs_data)
		current_price = float(get_latest_price(symbol=combined_symbol)['price'])
		rel_change = (hist_an['max']/hist_an['min']-1)*100 
		stability_score = abs(current_price-hist_an['average'])/(hist_an['max']-hist_an['min'])
		if (rel_change > max_change) and (stability_score<0.5):
			max_change = rel_change
			chosen_currency = combined_symbol
			stability_sc = stability_score
			average = hist_an['average']
			best_min, best_max = hist_an['min'], hist_an['max']
			chosen_cs_data = cs_data
	return {"chosen_currency": chosen_currency,
			 "max_change": max_change,
			 "stability_score": stability_sc,
			 "average": average,
			 "min": best_min,
			 "max": best_max,
			 "cs_data": chosen_cs_data[18:]
			}


if __name__ == "__main__":
	print(profit_calc(s1=1000, p2=1.8611, p1=1.8468))
	
	
def adasdasd():
	
	# Step 1: choose currency and get associated data
	chosen_currency_info = choose_currency_for_trading()
	print(chosen_currency_info)
	
	# Step 2: check if it makes sense to purchase
	cs_data_averages = get_cs_data_averages(cs_data=chosen_currency_info["cs_data"])
	forward_sensitivity = 3
	side = ["BUY"]
	safety_factor = 0.8
	decision = sunrays_based_descison(cs_data_averages=cs_data_averages,
								  forward_sensitivity=forward_sensitivity,
								  side=side,
								  safety_factor=safety_factor)
	print(decision)
	
	order_info = {"symbol": "TRXUSDT",
				  "side": "SELL",
				  "type": "MARKET",
				  "quantity": 1291.706}
