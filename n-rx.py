#                        _                  
#                       (_)                 
#  _ __   __ _ _   _ ___ _  ___ __ _  __ _  
# | '_ \ / _` | | | / __| |/ __/ _` |/ _` | 
# | | | | (_| | |_| \__ \ | (_| (_| | (_| | 
# |_| |_|\__,_|\__,_|___/_|\___\__,_|\__,_| 
#  
# licensed under the MIT license <http://opensource.org/licenses/MIT>

from config import NEXMO_CALLBACK_SECRET, DLR_KEY, INBOUND_KEY, INBOUNDCS_KEY, NEXMO_RANGES, DEV_RANGES, ADMIN_NUM, FILTERS_PATH

from flask import Flask, jsonify, request, abort
from redis import StrictRedis
from ipaddress import ip_address, ip_network
import logging, json

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
	logger.info("  stored delivery report for message %s in list [%s]" % (qs["messageId"], DLR_KEY))

def nmo_cmd(msg):
	if msg.get("msisdn", None) == ADMIN_NUM:
		keyword = msg.get("keyword", "") or msg.get("text", "").split(" ")[0]
		if keyword in ["n-tx", "n-rx"]:
			logger.info("  recieved command message from admin number (%s)" % (ADMIN_NUM))
			logger.info("    %s" % (msg["text"]))
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
			redis.rpush(INBOUNDCS_KEY, json.dumps(store))
			logger.info("  stored inbound command message %s in list [%s]" % (msg["messageId"], INBOUNDCS_KEY))
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
		logger.debug("filter %s matched message for application %s" % (f["filter_name"]), f["filter_for"])
		logger.info("  stored inbound command message %s in list [%s]" % (msg["messageId"], f["store_key"]))
		return True
	return False

def process_inbound(qs):
	if qs.get("concat", None):
		parts_lkey = "nsplit:%s" % (qs["concat-ref"])
		logger.debug("partial message, part %d of total %d, tmp list [%s]" % (message["concat-part"], message["concat-total"], parts_lkey))
		if qs["concat-part"] == qs["concat-total"]:
			# last part so lets combine them into one message!
			redis.lock(parts_lkey) # this is prob not needed...
			# these should be in the right order already... i think?
			parts = [json.loads(p.decote("utf-8")) for p in redis.lrange(parts_lkey, 0, -1)]
			body = "".join([p["text"] for p in parts])
			body += qs["text"]
			message = parts[0]
			message["text"] = body
			del message["concat-part"]
			redis.release(parts_lkey)
			redis.delete(parts_lkey)
			logger.info("  assembled split message %s" % (message["messageId"]))

			# check if its a nmo_cmd, if not pass to inbound queue
			if not nmo_cmd(message) and not sort_msg_into_redis(qs, inbound_filters):
				redis.rpush(INBOUND_KEY, json.dumps(message))
				logger.info("  stored unsorted inbound message %s in list [%s]" % (message["messageId"], INBOUND_KEY))
		else:
			redis.rpush(parts_lkey, json.dumps(qs))
			logger.info("  stored partial inbound message %d-%d in list [%s]" % (message["concat-part"], message["concat-total"], parts_lkey))	
	else:
		if not nmo_cmd(qs) and not sort_msg_into_redis(qs, inbound_filters):
			redis.rpush(INBOUND_KEY, json.dumps(qs))
			logger.info("  stored unsorted inbound message %s in list [%s]" % (qs["messageId"], INBOUND_KEY))

@app.before_request
def check_nexmo():
	if not any(ip_address(request.remote_addr) in ip_network(n) for n in NEXMO_RANGES+DEV_RANGES):
		logger.warning("request from invalid remote address (%s)" % (request.remote_addr))
		abort(403)

@app.route("/", methods=["GET"])
def index():
	if not NEXMO_CALLBACK_SECRET == request.args.get("nmo-secret", None):
		logger.warning("invalid NEXMO_CALLBACK_SECRET from %s" % (request.remote_addr))
		abort(403) # "bad boys bad boys whatcha gnna do"

	if request.args.get("status", None): # probably a dlr...
		logger.info("recieved an delivery report")
		process_dlr(request.args)
		return ""
	elif request.args.get("type", None): # probably an inbound
		logger.info("recieved an inbound message")
		process_inbound(request.args)
		return ""
	else:
		return "idk"

app.run(host="10.0.0.5")