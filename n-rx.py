from flask import Flask, jsonify, request

SPLITMSG_KEY = "nsplit"
DLR_KEY = "ndlr"
INBOUND_KEY = "ninbound"

NEXMO_RANGES = [
	"174.37.245.32/29",
	"174.36.197.192/28",
	"173.193.199.16/28",
	"119.81.44.0/28"
]

app = Flask(__name__)

def combine_split(parts):
	pass

def process_dlr(qs):
	pass

def process_inbound(qs):
	pass

@app.before_request
def check_nexmo():
	if not all(ip_address(request.remote_addr) in ip_network(n) for n in NEXMO_RANGES):
		return 403, "bad boys bad boy whatcha gnna do"

@app.route("/")
def index():
	if request.args.get("status", None): # probably a dlr...
		# check req

		process_dlr(request.args)
		return 200
	else: # probably an inbound
		#check req

		process_inbound(request.args)
		return 200
