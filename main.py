from Trader import Trader
from BinanceAPI import BinanceAPI
from RTObserver import RTObserverRunner
import os


# TODO stop loss to prevent profit plummeting
# TODO take-profit sell (3:1) rule
# TODO handle failures in transactions

if __name__ == "__main__":
	# trader = Trader()
	public_key = os.environ.get("PUBLIC_KEY", default=None)
	secret_key = os.environ.get("SECRET_KEY", default=None)

	rto = RTObserverRunner(symbol="EOSUSDT",
						   purchase_price=0,
						   purchase_quantity=0,
						   order_id=125721695,
						   stop_loss_price=3,
						   public_key=public_key,
						   secret_key=secret_key)
	rto.start()


