import os

API_KEY = os.environ.get("NMO_KEY")
API_SECRET = os.environ.get("NMO_SECRET")

NEXMO_CALLBACK_SECRET = os.environ.get("NMO_CB_SECRET")
NEXMO_RANGES = [
	"174.37.245.32/29",
	"174.36.197.192/28",
	"173.193.199.16/28",
	"119.81.44.0/28"
]
DEV_RANGES = [
	"192.168.1.0/24"
]

ADMIN_NUM = os.environ.get("NMO_ADMIN_NUM")

DLR_KEY = "ndlr"
DLRCS_KEY = "ndlrcs"
INBOUND_KEY = "ninbound"
INBOUNDCS_KEY = "ninboundcs"
SEND_KEY = "ntosend"
SENTCS_KEY = "nsentcs"
ERROR_KEY = "nerrord"

SENTCS_PATH = "n_sent_coldstore.js"
INBOUNDCS_PATH = "n_inbound_coldstore.js"

STORE_INTERVAL = 3600

FILTERS_PATH = "inbound_filters.json"
