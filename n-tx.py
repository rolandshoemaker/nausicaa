#!/usr/bin/python3
import libnmo

import json, os, logging
from redis import StrictRedis
from datetime import datetime

API_KEY = os.environ.get("NMO_KEY")
API_SECRET = os.environ.get("NMO_SECRET")

SEND_KEY = "ntosend"
ERROR_KEY = "nerrored"

SENT_COLDSTORE = "n_tx_sent.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
	redis = StrictRedis()
	nm = libnmo.Nexmo(API_KEY, API_SECRET)
	logger.info("started! ^_^")
	logger.info("  starting balance: %f" % (nm.balance))
	logger.info("  current send list size: %d" % (redis.llen(SEND_KEY)))
	logger.info("  current error list size: %d" % (redis.llen(ERROR_KEY)))

	while True:
		j_msg = json.loads(redis.blpop(SEND_KEY))
		logger.info("processing new message (%s->%s)" % (j_msg["from"], j_msg["to"]))
		logger.debug("  body: %s" % (j_msg["body"]))
		message = libnmo.NexmoMessage.new_text(j_msg["from"], j_msg["to"], j_msg["body"])
		logger.debug("  created message")
		responses = nm.send_msg(message)
		# scrub api key and secret from cold store
		logger.debug("  sent request to nexmo")
		del message["api_key"]
		del message["api_secret"]
		thing = {
			"at": datetime.utcnow().isoformat()+"UTC",
			"message": message,
			"responses": responses
		}

		if any(int(r["status"]) > 0 for r in responses["messages"]):
				# bad times :<
			for r in responses["messages"]:
				if r["status"] > 0:
					logger.error("    sending message failed, %s" % (r["error-text"]))
			logger.info("  added message to error list (%s)" % (ERROR_KEY))
			redis.rpush(ERROR_KEY, json.dumps(thing))
			continue

		logger.info("  message sent (%d parts), current balance: %d" % (responses["message-count"], nm.balance))

		with open(SENT_COLDSTORE, "r") as cold_f:
			cold = json.load(cold_f)
		cold.append(thing)
		with open(SENT_COLDSTORE, "w") as cold_f:
			json.dump(cold, cold_f)
		logger.debug("  saved message and responses to outbound coldstore (%s)" % (SENT_COLDSTORE))
		logger.debug("finished processing message")

run()
