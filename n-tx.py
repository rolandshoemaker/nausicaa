#!/usr/bin/python3
import libnmo

import json
from redis import StrictRedis
from datetime import datetime

API_KEY = ""
API_SECRET = ""

SEND_KEY = "ntosend"
ERROR_KEY = "nerrored"

SENT_COLDSTORE = "n_tx_sent.json"

def log(msg, level="info"):
	print("n-tx [%sUTC] %s: %s" % (level, datetime.utcnow().isoformat(), msg))

def run():
	redis = redis.StrictRedis()
	nm = libnmo.Nexmo(API_KEY, API_SECRET)
	log("started! ^_^")
	log("  starting balance: %d" % (nm.balance))
	log("  current send list size: " % (redis.llen(SEND_KEY)))
	log("  current error list size: " % (redis.llen(ERROR_KEY)))


	while True:
		j_msg = json.loads(redis.blpop(SEND_KEY))
		log("processing new message")
		log("  from: %s", level="debug")
		log("  to: %s", level="debug")
		log("  body: %s", level="debug")
		message = libnmo.NexmoMessage.new_text(j_msg["from"], j_msg["to"], j_msg["body"])
		log("  created message", level="debug")
		responses = nm.send_msg(message)
		# scrub api key and secret from cold store
		log("  sent request to nexmo", level="debug")
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
					log("    sending message failed, %s" % (r["error-text"]), level="ERROR")
			log("  added message to error list (%s)" % (ERROR_KEY))
			redis.rpush(ERROR_KEY, json.dumps(thing))
			continue

		log("  message sent (%d parts), current balance: %d" % (responses["message-count"], nm.balance))

		with open(SENT_COLDSTORE, "r") as cold_f:
			cold = json.load(cold_f)
		cold.append(thing)
		with open(SENT_COLDSTORE, "w") as cold_f:
			json.dump(cold, cold_f)
		log("  saved message and responses to outbound coldstore (%s)" % (SENT_COLDSTORE))

		log("finished processing message")
