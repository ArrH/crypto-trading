import time
import hashlib
import hmac
import requests
from urllib.parse import urlencode
import json

def get_time_in_ms():
	return int(time.time()*1000)


def build_query_params_string(query_params):
	query_params_string = ""
	for key, value in query_params.items():
		query_params_string+="{key}={value}&".format(key=key, value=value)
	return query_params_string[:-1]
	
	
def build_endpoint_url(endpoint):
	return "https://api.binance.com{endpoint}".format(endpoint=endpoint)


def build_request_url(endpoint, query_params=None):
	request_url = build_endpoint_url(endpoint=endpoint)
	if query_params is not None:
		request_url += "?" + build_query_params_string(query_params)
	return request_url
	
	
def make_public_request(endpoint, query_params=None):
	request_url = build_request_url(endpoint=endpoint, query_params=query_params)
	r = requests.get(url=request_url)
	return json.loads(r.text)

	
def make_private_request(method, endpoint, query_params=None):
	secret_key = "2nryuByqkdRDad4jlsowQijRhIILix2xI5aAs7b8M8hlccVckq3MRy6xbFqroWW4"
	public_key = "H3XVJr9aBI3t2XnpI8JdNXteAJCRhGDjlSOmAupFN1IrSbCfattnlZ2TNlUHlcUK"

	# Build the basic required params dict and put it into url encode
	if query_params is None:
		query_params = {}
	query_params["timestamp"] = get_time_in_ms()
	params = urlencode(query_params)
	
	# Creat the signature	
	hashedsig = hmac.new(secret_key.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
	
	headers = {"X-MBX-APIKEY" : public_key}
	
	request_url = build_endpoint_url(endpoint=endpoint) + "?" + params + "&signature={hashedsig}".format(hashedsig=hashedsig)
	print(request_url)
	if method == "POST":
		r = requests.post(url=request_url, headers=headers)
	else:
		r = requests.get(url=request_url, headers=headers)
	return json.loads(r.text)
	
	
def check_free_balances_for_currency_list(account_info, currency_list):
	free_balances = {}
	if account_info["canTrade"]:
		balances = account_info["balances"]
		for balance in balances:
			if balance["asset"] in currency_list:
				free_balances[balance["asset"]] = balance["free"]
	return free_balances


def compound_visualizer():
	your_sum = 1000
	days = 365+10
	gain_after_sell = 2/1000.
	sales_per_day = 4
	for i in range(days):
		for k in range(sales_per_day):
			your_sum += your_sum * gain_after_sell
	print(your_sum, your_sum/100*100, 4/1000.)

	
def profit_calc(s1, p2, p1, f=0.1):
	f = f/100
	return s1*(p2/p1 * (1-f)**2 - 1)

	
def check_profitability(p2, p1, margin, f=0.1):
	f = f/100
	margin = margin/100*2
	if p2/p1 > (margin+1)/((1-f)**2):
		return True
	else:
		return False
		
def cs_history_analysis(cs_data):
	per_min = 10000000.
	per_max = 0.
	per_average = 0.
	for i in range(len(cs_data)):
		current = float(cs_data[i][4])
		per_max = max([per_max, current])
		per_min = min([per_min, current])
		per_average += current
	per_average = per_average/len(cs_data)
	return {"max": per_max, "min": per_min, "average": per_average}
	
	
def get_cs_data_averages(cs_data):
	cs_data_averages = []
	for i in range(len(cs_data)):
		cs_data_averages.append((float(cs_data[i][1])+float(cs_data[i][4]))/2)
	return cs_data_averages

	
def sunrays_based_descison(cs_data_averages, forward_sensitivity, side, safety_factor):
	
	heights_list = []
	for i in range(1, forward_sensitivity+2):
		heights_list.append(cs_data_averages[-i]-cs_data_averages[0])
	print(heights_list)
	
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

	if abs(heights_list[-1]) >= (safety_factor*(max(cs_data_averages) - min(cs_data_averages))):
		decision = True
	else: 
		return False
		
	if decision == True:	
		for i in range(forward_sensitivity):
			if abs(heights_list[i]) < abs(heights_list[i+1]):
				decision = True
			else:
				return False
	
	return decision
		
		
		
