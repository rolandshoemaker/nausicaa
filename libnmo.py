#!/usr/bin/python3
import requests
import json

from urllib.parse import urlencode

BASE_URL = "https://rest.nexmo.com"
RESP_TYPE = "json"
M_TYPES = [
	"text",
	"unicode",
	"wap",
	"binary",
	"vcal",
	"vcard"
]

def send_request(url, method="post", url_args=None, json_data=None):
	if method == "get":
		if url_args:
			url = "%s?%s" % (url, urlencode(url_args))
		r = requests.get(url)
		if not r.status_code == 200:
			raise ValueError # or you know something proper...
		return r.json()
	elif method =="post": # doesn't cover binary uploads yet as far as i knowssss?
		if not json_data:
			raise ValueError # yerp... right thing
		h = {"content-type": "application/json"}
		r = requests.post(url, data=json.dumps(json_data), headers=h)
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

	def send_msg(self, send_from, send_to, body):
		msg = {
			"from": send_from,
			"to": send_to,
			"type": "text", # "unicode",
			"text": body, # body of the message if a text (not binary/wap)
			"status-report-req": 0, # DLR
			"client-ref": "libnmo", # who diddit
			"network-code": "", # specific network, MCCMNC
			"vcard": "", # vcard body
			"vcal": "", # vcal body
			"ttl": 0, # message 'life span'?
			"message-class": 0, # set to zero for FLASH msg
			# binary spec
			"body": 0, # hex encoded binary
			"udh": 0 # hex encoded udh (idk what that is...)
		}

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

class NexmoMessage(object):
	msg = None

	def __init__(self, msg):
		self.msg = msg

	@static_method
	def new_text(send_from, send_to, body, client_ref=None, status_report_req=False, flash_message=False):
		try:
			body.decode("ascii")
			text_type = "text"
		except UnicodeDecodeError:
			text_type = "unicode"
		# basic message structure for now...
		msg = {
			"from": send_from,
			"to": send_to,
			"type": text_type, # "unicode",
			"text": body, # body of the message if a text (not binary/wap)
			"status-report-req": 0, # DLR
			"client-ref": "libnmo", # who diddit
			"message-class": 0, # set to zero for FLASH msg
		}
		if client_ref:
			msg["client-ref"] = client_ref
		if status_report_req:
			msg["status-report-req"] = 1
		if flash_message:
			msg["message-class"] = 0

		formed_msg = NexmoMessage(msg)
		if formed_msg.validate():
			return formed_msg

	def validate(self):
		return True
