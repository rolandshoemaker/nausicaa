#!/usr/bin/python3
# archiver
from config import STORE_INTERVAL, SENTCS_KEY, DLRCS_KEY, INBOUNDCS_KEY, SENTCS_PATH, INBOUNDCS_PATH

import json
from time import sleep
from redis import StrictRedis

def load_cs(where):
	with open(where "r") as f:
		insides = json.load(f)
	return insides

def update_cs(what, where):
	with open(where, "w") as f:
		json.dump(what, f)

def consume(cs, key, cs_path):
	if redis.llen(key) > 0:
			redis.lock(key)
			things = redis.lrange(key, 0, -1)
			cs += [json.loads(t) for t in things]
			update_cs(cs, cs_path)
			# idk if you can do it in this order... would be nice
			redis.delete(key)
			redis.release(key)

def run():
	redis = StrictRedis()
	coldstore = load_cs(SENTCS_PATH)

	while True:
		consume(coldstore, SENTCS_KEY, SENTCS_PATH)
		consume(coldstore, INBOUNDCS_KEY, INBOUNDCS_PATH)

		sleep(STORE_INTERVAL)
