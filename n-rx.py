from config import NEXMO_CALLBACK_SECRET, DLR_KEY, INBOUND_KEY, INBOUNDCS_KEY, NEXMO_RANGES, DEV_RANGES, ADMIN_NUM

from flask import Flask, jsonify, request
from redis import StrictRedis
import logging

app = Flask(__name__)
redis = StrictRedis()
with open(FILTERS_PATH, "r") as f:
	inbound_filters = json.load(f)

formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=formatter, level="INFO")
logger = logging.getLogger("n-rx")

def combine_split(parts):
	pass

def process_dlr(qs):
	# pretty simple
	redis.rpush(DLR_KEY, json.dumps(qs))

def nmo_cmd(msg):
	if msg.get("msisdn", "") == ADMIN_NUM:
		keyword = msg.get("keyword", "") or msg.get("text", "").split(" ")[0]
		if keyword in ["n-tx", "n-rx"]:
			command = msg.get("text", "").split(" ")[1]
			args = msg.get("text", "").split(" ")[2:]
			if keyword == "n-tx":
				pass
			elif keyword == "n-rx":
				pass

			store = {
				"app": "n-rx",
				"message": msg
			}
			redis.rpush(INBOUNDCS_KEY, store)
			return True

def sort_msg_into_redis(msg, filters):
	for f in filters:
		specifics = [f[s] == msg.get(s) for s in ["msisdn", "to", "type"] if f.get(s, None)]
		if not all(specifics):
			continue
		if f.get("keyword"):
			if not msg.get("text", None):
				continue
			keyword = msg.get("keyword", None) or msg.get("text", "").split(" ")[0]
			if not keyword == f["keyword"]:
				continue
		if f.get("text_contains", None):
			if not msg.get("text", None):
				continue
			pass

		# if we got here everything should've matched
		redis.rpush(f["store_key"], json.dumps(msg))
		return True
	return False


# instead of coldstoring any of this individual applications should iterate through
# the lists themselves and process/coldstore the dlr's and inbound messages that they
# expect to see and ignore the rest. (except nmo commands, we will coldstore those in
# nmo_cmd()...)

# this should also have something like filter() that can take a json format file and
# sort inbound messages into certain redis lists based on filters...
def process_inbound(qs):
	if qs.get("concat", None):
		parts_lkey = "nsplit:%s" % (qs["concat-ref"])
		if qs["concat-part"] == qs["concat-total"]:
			# last part so lets combine them into one message!
			redis.lock(parts_lkey) # this is prob not needed...
			# these should be in the right order already... i think?
			parts = [json.loads(p) for p in redis.lrange(parts_lkey, 0, -1)]
			body = "".join([p["text"] for p in parts])
			body += qs["text"]
			message = parts[0]
			message["text"] = body
			del message["concat-part"]
			redis.release(parts_lkey)
			redis.delete(parts_lkey)
			# check if its a nmo_cmd, if not pass to inbound queue
			if not nmo_cmd(message) and not sort_msg_into_redis(qs, inbound_filters):
				redis.rpush(INBOUND_KEY, json.dumps(message))
		else:
			redis.rpush(parts_lkey, json.dumps(qs))
	else:
		if not nmo_cmd(qs) and not sort_msg_into_redis(qs, inbound_filters):
			redis.rpush(INBOUND_KEY, json.dumps(qs))

@app.before_request
def check_nexmo():
	if not all(ip_address(request.remote_addr) in ip_network(n) for n in NEXMO_RANGES+DEV_RANGES):
		abort(403)

@app.route("/", methods=["GET"])
def index():
	if not NEXMO_CALLBACK_SECRET == reqest.args.get("nmo-secret", None):
		abort(403) # "bad boys bad boys whatcha gnna do"

	if request.args.get("status", None): # probably a dlr...
		process_dlr(request.args)
		return 200
	else: # probably an inbound
		process_inbound(request.args)
		return 200
