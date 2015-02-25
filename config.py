#                        _                  
#                       (_)                 
#  _ __   __ _ _   _ ___ _  ___ __ _  __ _  
# | '_ \ / _` | | | / __| |/ __/ _` |/ _` | 
# | | | | (_| | |_| \__ \ | (_| (_| | (_| | 
# |_| |_|\__,_|\__,_|___/_|\___\__,_|\__,_| 
#  
# licensed under the MIT license <http://opensource.org/licenses/MIT>

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
	"10.0.0.0/24"
]

ADMIN_NUM = os.environ.get("NMO_ADMIN_NUM")

DLR_KEY = "ndlr"
DLRCS_KEY = "ndlrcs"
INBOUND_KEY = "ninbound"
INBOUNDCS_KEY = "ninboundcs"
SEND_KEY = "ntosend"
SENTCS_KEY = "nsentcs"
ERROR_KEY = "nerrord"

SENTCS_PATH = "n_sent_coldstore.json"
INBOUNDCS_PATH = "n_inbound_coldstore.json"

STORE_INTERVAL = 3600

FILTERS_PATH = "inbound_filters.json"
