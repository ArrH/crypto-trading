from Trader import Trader
from BinanceAPI import BinanceAPI


# TODO stop loss to prevent profit plummeting
# TODO take-profit sell (3:1) rule
# TODO handle failures in transactions

if __name__ == "__main__":
	trader = Trader()


	# start_sunray_trading()
	# print(modify_amount_to_lot_size(amount_float=12.223,
	# 						  lot_size=5))

	# # print(compound_visualizer())
	#
	# market_data = get_market_data()
	# lot_size_dict = build_lot_size_dict(market_data=market_data)
	#
	# side = 'BUY'
	# account_info = get_account_information()
	# order_amount = float(check_free_balances_for_currency_list(account_info=account_info,
	# 															  currency_list=['USDT'])['USDT'])
	# print(order_amount)
	# order_amount = float(order_amount) / float(get_latest_price(symbol='VETUSDT')['price'])
	# # order_amount *= 0.9999
	# print(order_amount)
	#
	# # order_amount = round(order_amount, lot_size_dict['ETHUSDT'])
	# order_amount = modify_amount_to_lot_size(amount_float=order_amount,
	# 										 lot_size=lot_size_dict['VETUSDT'])
	# print(order_amount)
	# order_data = place_order(symbol='ETHUSDT',
	# 							  side=side,
	# 							  o_type="MARKET",
	# 						 	  quantity=order_amount)
	# print(order_data)
	#

