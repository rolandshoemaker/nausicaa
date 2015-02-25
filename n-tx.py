#!/usr/bin/python3
import libnmo
from config import API_KEY, API_SECRET, SEND_KEY, ERROR_KEY, SENTCS_KEY

import json, os, logging
from redis import StrictRedis
from datetime import datetime
from time import sleep

formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=formatter, level="INFO")
logger = logging.getLogger("n-tx")

def run():
	redis = StrictRedis()
	nm = libnmo.Nexmo(API_KEY, API_SECRET)
	logger.info("started! ^_^")
	logger.info("  starting balance: %f" % (nm.balance))
	logger.info("  current send list size: %d" % (redis.llen(SEND_KEY)))
	logger.info("  current error list size: %d" % (redis.llen(ERROR_KEY)))
	logger.info("  current sent coldstore list size: %d" % (redis.llen(SENTCS_KEY)))

	while True:
		if redis.get("ncooldown"):
			sleep(30)
		else:
			j_msg = json.loads(redis.blpop(SEND_KEY))
			logger.info("processing new message (%s->%s)" % (j_msg["from"], j_msg["to"]))
			logger.debug("  body: %s" % (j_msg["body"]))
			message = libnmo.NexmoMessage.new_text(j_msg["from"], j_msg["to"], j_msg["body"])
			logger.debug("  created message")
			responses = nm.send_msg(message, client_ref=j_msg.get("app", None), status_report_req=j_msg.get("dlr", False), flash_message=j_msg.get("flash", False))
			# scrub api key and secret from coldstore/error object
			logger.debug("  sent request to nexmo")
			del message["api_key"]
			del message["api_secret"]
			thing = {
				"at": datetime.utcnow().isoformat()+"UTC",
				"message": message,
				"responses": responses["messages"]
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
			redis.rpush(SENTCS_KEY, json.dumps(thing))
			logger.debug("  saved message and responses to outbound coldstore list (%s)" % (SENT_COLDSTORE))
			logger.debug("finished processing message")

run()
