from .tunet import get_challenge, login, logout, net_status, auth_status

from time import sleep

import logging
logger = logging.getLogger(__name__)

### source repo 
# https://github.com/yf-yang/Spark319_AutoConnect

### author
# YangYiFei spark11
# Thanks to Zhao WenLiang [spark12] for assisting debug.
# Thanks to Wang QiRui
# ref: https://github.com/wangqr/tunet2018

### configurations
# allow other users to stay for at most TIME_LIMIT mins
# to avoid wasting their balance.
TIME_LIMIT=30

# interval in seconds between logout and login
SLEEP_INTERVAL=10

# max number of retry every time
MAX_RETRY=1

### constants
# standard account username and md5
ACCOUNT_FILE='/etc/.auto_connect.cfg'

### utilities
# acquire username and password
def account():
    with open(ACCOUNT_FILE) as f:
        username, passwd = [x.strip() for x in f.readlines()]
    return username, passwd

# functions
def try_login():
    try:
        username, passwd = account()
    except IOError:
        logger.error("Unable to retrieve username and password. Are you root?")
    ch = get_challenge(username)
    if ch is not None:
        r = login(username, passwd, ch['challenge'])
        if r is not None:
            logger.info("Connected to the network.")
        else:
            logger.error("Failed to connect to the network.")
    else:
        logger.error("Failed to acquire challenge.")

def try_logout(username):
    ch = get_challenge(username)
    if ch is not None:
        logout(username, ch['challenge'])
    else:
        logger.error("Failed to acquire challenge.")

def try_reconnect(username):
    try_logout(username)
    sleep(SLEEP_INTERVAL)
    try_login()

def main():
    try: 
        try:
            unlimited_username, _ = account()
        except IOError:
            logger.error("Unable to retrieve username and password. "
                "Are you root?")
        for ntry in range(MAX_RETRY):
            # acquire statistics
            s = net_status()
            if s:
                # online
                (
                    username, # 0
                    logintime, # 1 (second)
                    currenttime, # 2 (second)
                    _, 
                    _, 
                    _, 
                    usage, # 6 (Bytes)
                    _,
                    ip, # 8
                    _,
                    _,
                    _,
                    _,
                ) = s

                ### switch units
                # time elapsed in minutes
                time = (float(currenttime) - float(logintime)) / 60
                # network traffic usage in GB
                usage = float(usage) / 1024 / 1024 / 1024
                logger.info("Online. USERNAME:%s IP:%s TIME:%.3f(min) "
                    "USAGE:%.3f(GB)" % (username, ip, time, usage))

                # allow non-standard users to connect in case the unlimited 
                # account is banned or expires
                if username != unlimited_username:
                    logger.warning("Unexpected user %s" % username)
                    # Do not allow a non-standard user to connect for too long 
                    # to avoid wasting their balance.
                    if time > TIME_LIMIT:
                        logger.warning("%s is online for more than %s mins. "
                            "Try to reconnect..." % (username, TIME_LIMIT))
                        try_reconnect(username)
            else:
                # offline
                logger.info("Offline. #%d/%d try to reconnect..." 
                    % (ntry+1, MAX_RETRY))
                username = auth_status()
                if username:
                    try_reconnect(username) 
                else:
                    try_login()
    except:
        logger.critical("Fatal bug:", exc_info=True)
