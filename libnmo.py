#!/usr/bin/python3
import requests
import json

from urllib.parse import urlencode, quote

BASE_URL = "https://rest.nexmo.com"
RESP_TYPE = "json"

def send_request(url, method="post", url_args=None, json_obj=None):
	if url_args:
		url = "%s?%s" % (url, urlencode(url_args))
	if method == "get":
		r = requests.get(url)
		if not r.status_code == 200:
			raise ValueError # or you know something proper...
		return r.json()
	elif method =="post":
		r = requests.post(url)
		if not r.status_code == 200:
			raise ValueError # ...
		return r.json()

def validate_msg(msg):
	pass

class Nexmo(object):
	key = None
	secret = None
	balance = None
	numbers = None

	def __init__(self, key, secret):
		if not key or not secret:
			raise ValueError # but actually something better...
		self.key = key
		self.secret = secret
		self.update_balance()
		self.update_numbers()

	def update_balance(self):
		resp = send_request("%s/account/get-balance" % (BASE_URL), method="get", url_args={"api_key": self.key, "api_secret": self.secret})
		self.last_balance = resp["value"]
		self.balance = resp["value"]

	def update_numbers(self, index=1, size=10, pattern=None, search_pattern=None):
		req_args = {
			"api_key": self.key,
			"api_secret": self.secret,
			"index": index,
			"size": size
		}
		if pattern:
			req["pattern"] = pattern
		if search_pattern:
			req["search_pattern"] = search_pattern
		resp = send_request("%s/account/numbers" % (BASE_URL), method="get", url_args=req_args)
		self.numbers = [NexmoNumber(n["msisdn"], n["type"], n["country"], n["features"]) for n in resp["numbers"]]

	def send_msg(self, message):
		message["api_key"] = self.key
		message["api_secret"] = self.secret

		resp = send_request("%s/sms/%s" % (BASE_URL, RESP_TYPE), url_args=message)
		self.update_balance()
		return resp["messages"]

class NexmoNumber(object):
	msisdn = None
	n_type = None
	country = None
	features = None

	def __init__(self, msisdn, n_type, country, features):
		self.msisdn = msisdn
		self.n_type = n_type
		self.country = country
		self.features = features

# msg = {
# 	"from": send_from,
# 	"to": send_to,
# 	"type": "text", # "unicode",
# 	"text": body, # body of the message if a text (not binary/wap)
# 	"status-report-req": 0, # DLR
# 	"client-ref": "libnmo", # who diddit
# 	"network-code": "", # specific network, MCCMNC
# 	"vcard": "", # vcard body
# 	"vcal": "", # vcal body
# 	"ttl": 0, # message 'life span'?
# 	"message-class": 0, # set to zero for FLASH msg
# 	# binary spec
# 	"body": 0, # hex encoded binary
# 	"udh": 0 # hex encoded udh (idk what that is...)
# }

class NexmoMsg(object):
	@staticmethod
	def new_text(send_from, send_to, body, client_ref=None, status_report_req=False, flash_message=False):
		if len(body) > 3200:
			raise ValueError # ....
		try:
			body.encode("ascii")
			text_type = "text"
		except UnicodeEncodeError:
			text_type = "unicode"
			# body = quote(body)

		# basic message structure for now...
		msg = {
			"from": send_from,
			"to": send_to,
			"type": text_type, # "unicode",
			"text": body, # body of the message if a text (not binary/wap)
			"client-ref": "libnmo", # who diddit
		}
		if client_ref:
			msg["client-ref"] = client_ref
		if status_report_req:
			msg["status-report-req"] = 1
		if flash_message:
			msg["message-class"] = 0 # this does weird things atm, idk...

		return msg
