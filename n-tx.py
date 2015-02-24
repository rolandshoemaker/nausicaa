#!/usr/bin/python3
import libnmo

import json
from redis import StrictRedis
from datetime import datetime

API_KEY = ""
API_SECRET = ""

SEND_KEY = "ntosend"
ERROR_KEY = "nerrored"

SENT_COLDSTORE = "n_sent.json"

def run():
	redis = redis.StrictRedis(host=)
	nm = libnmo.Nexmo(API_KEY, API_SECRET)

	while True:
		j_msg = json.loads(redis.blpop(SEND_KEY))
		message = libnmo.NexmoMessage.new_text(j_msg["from"], j_msg["to"], j_msg["body"])
		responses = nm.send_msg(message)
		# scrub api key and secret from cold store
		del message["api_key"]
		del message["api_secret"]
		thing = {
			"at": datetime.utcnow().isoformat()+" UTC",
			"message": message,
			"responses": responses
		}
		if any(int(r["status"]) > 0 for r in responses):
			redis.rpush(ERROR_KEY, json.dumps(thing))
			continue

		with open("SENT_COLDSTORE", "rw") as cold_f:
			cold = json.load(cold_f)
			cold.append(thing)
			json.dump(cold, cold_f)
