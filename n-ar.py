#!/usr/bin/python3
#                        _                  
#                       (_)                 
#  _ __   __ _ _   _ ___ _  ___ __ _  __ _  
# | '_ \ / _` | | | / __| |/ __/ _` |/ _` | 
# | | | | (_| | |_| \__ \ | (_| (_| | (_| | 
# |_| |_|\__,_|\__,_|___/_|\___\__,_|\__,_| 
#  
# licensed under the MIT license <http://opensource.org/licenses/MIT>
#
# archiver

from config import STORE_INTERVAL, SENTCS_KEY, DLRCS_KEY, INBOUNDCS_KEY, SENTCS_PATH, INBOUNDCS_PATH

import json
from time import sleep
from redis import StrictRedis

redis = StrictRedis()

def load_cs(where):
	try:
		with open(where, "r") as f:
			insides = json.load(f)
		return insides
	except FileNotFoundError:
		return []

def update_cs(what, where):
	with open(where, "w") as f:
		json.dump(what, f)

def consume(cs, key, cs_path):
	if redis.llen(key) > 0:
			lock = redis.lock(key)
			things = redis.lrange(key, 0, -1)
			cs += [json.loads(t.decode("utf-8")) for t in things]
			update_cs(cs, cs_path)
			# idk if you can do it in this order... would be nice
			lock.release()
			redis.delete(key)

def run():
	coldstore = load_cs(SENTCS_PATH)

	while True:
		consume(coldstore, SENTCS_KEY, SENTCS_PATH)
		consume(coldstore, INBOUNDCS_KEY, INBOUNDCS_PATH)

		sleep(STORE_INTERVAL)

run()