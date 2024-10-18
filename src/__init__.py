import random
from datetime import datetime
from json.decoder import JSONDecodeError
from .deeplchain import (log, log_line, reset, number, read_config, countdown_timer,
                             hju, mrh, htm, kng, bru, pth, awak, clear, banner, log_error)
from requests.exceptions import ConnectionError, Timeout, ProxyError, RequestException, HTTPError