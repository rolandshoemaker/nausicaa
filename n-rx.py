from flask import Flask, jsonify, request
from redis import StrictRedis

# instead of coldstoring any of this individual applications should iterate through
# the lists themselves and process/coldstore the dlr's and inbound messages that they
# expect to see and ignore the rest.
DLR_KEY = "ndlr"
INBOUND_KEY = "ninbound"

NEXMO_RANGES = [
	"174.37.245.32/29",
	"174.36.197.192/28",
	"173.193.199.16/28",
	"119.81.44.0/28"
]

DEV_RANGES = [
	"192.168.1.0/24"
]

app = Flask(__name__)
redis = redis.StrictRedis()

def combine_split(parts):
	pass

def process_dlr(qs):
	# pretty simple
	redis.rpush(DLR_KEY, json.dumps(qs))

def process_inbound(qs):
	if qs.get("concat", None):
		parts_lkey = "nsplit:%s" % (qs["concat-ref"])
		if qs["concat-part"] == qs["concat-total"]:
			# last part so lets combine them into one message!
			redis.lock(parts_lkey) # this is prob not needed...
			# these should be in the right order already... i think?
			parts = [json.loads(p) for p in redis.lrange(parts_lkey, 0, -1)]
			body += qs["text"]
			message = parts[0]
			message["text"] = body
			del message["concat-part"]
			redis.release(parts_lkey)
			redis.delete(parts_lkey)
			redis.rpush(INBOUND_KEY, message)
		else:
			redis.rpush(parts_lkey, json.dumps(qs))
	else:
		redis.rpush(INBOUND_KEY, json.dumps(qs))

@app.before_request
def check_nexmo():
	if not all(ip_address(request.remote_addr) in ip_network(n) for n in NEXMO_RANGES+DEV_RANGES):
		return 403, "bad boys bad boys whatcha gnna do"

@app.route("/", methods=["GET"])
def index():
	if request.args.get("status", None): # probably a dlr...
		# check req

		process_dlr(request.args)
		return 200
	else: # probably an inbound
		#check req

		process_inbound(request.args)
		return 200
