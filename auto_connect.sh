#!/bin/bash

### source repo 
# https://github.com/yf-yang/Spark319_AutoConnect

### author
# YangYiFei spark11
# Thanks to Zhao WenLiang [spark12] for assisting debug.
# Thanks to Gu ZhaoYuan [spark10] for his codes.
# ref: https://github.com/guzhaoyuan/net.tsinghua/blob/master/linux/netTHU

### configurations
# allow other users to stay for at most TIME_LIMIT mins
# to avoid wasting their balance.
TIME_LIMIT=30

# interval in seconds between logout and login
SLEEP_INTERVAL=20

# max number of retry every time
MAX_RETRY=5

### constants
# standard account username and md5
ACCOUNT_FILE=/etc/.auto_connect.cfg

# statistic page URL
STATUS_URL=https://net.tsinghua.edu.cn/cgi-bin/rad_user_info

# login page URL
LOGIN_URL=net.tsinghua.edu.cn/do_login.php

# log file
LOG_FILE=/tmp/auto_connect.log

### utilities
# utilities for logging
function getCurrentTime {
    date "+%y/%m/%d %T.%3N"
}

# invoke python to execute math operations
function py {
    echo "print($1)" | python3
}

# logger
function LOG {
    echo "`getCurrentTime` $1" >> $LOG_FILE
}

function INFO {
    LOG "[   INFO] $1"
}

function WARNING {
    LOG "[WARNING] $1"
}

function ERROR {
    LOG "[  ERROR] $1"
}

### functions
# get current network status
# arg $1 - username
# arg $2 - login time in seconds (since the epoch)
# arg $3 - current time in seconds (since the epoch)
# arg $7 - network traffic usage in Bytes
# arg $8 - total time usage in seconds
# arg $9 - IP address
# arg $12 - balance of the account in Yuan
function getStatus {
    response=$(curl -s --connect-timeout 5 --get $STATUS_URL)
    # Disconnect or Timeout
    if [ -z $response ]; then
        echo 
    else
        echo $response | awk -F, '{print $1,$2,$3,$7,$9}'
    fi
}

function logout {
    curl -L $LOGIN_URL --data "action=logout"
}

function login {
    read USERNAME MD5 <<< `cat $ACCOUNT_FILE`
    result=$(curl -sL $LOGIN_URL --data "action=login&username="$USERNAME"&password={MD5_HEX}"$MD5"&ac_id=1")
    status=`echo $result |awk '{print $3}'`
    if [ $status != "successful." ]; then
        error=`echo $result | awk '{print $1}'`
    fi
    if [[ $error == "E2532:" ]]; then
        ERROR "(E2532) Failed to connect: Login too frequently."
    elif [[ $error == "E2553:" ]]; then
        ERROR "(E2553) Failed to connect: Invalid Account"
    fi
}

# logout from current network, then login
function reconnect {
    logout
    sleep $SLEEP_INTERVAL
    login
    echo
}

### main
read UNLIMITED_USERNAME MD5 <<< `cat $ACCOUNT_FILE`
for try in {1..$MAX_RETRY}
do
    status=$(getStatus)
    if [ -z "$status" ]; then
        INFO "Offline. #$try/5 Try to reconnect..."
        login
    else
        # load status into variables
        read -r username logintime currenttime usage ip <<<$(echo $status)
        # convert time to min
        time=$(py "'%.3f' % (($currenttime-$logintime)/60)")

        # convert network usage to GB
        usage=$(py "'%.3f' % ($usage/1024/1024/1024)")
        INFO "Online. USERNAME:$username IP:$ip TIME:$time(min) USAGE:$usage(GB)"

        # allow non-standard users to connect in case the unlimited account is
        # banned or expires
        if [[ $username != $UNLIMITED_USERNAME ]]; then
            WARNING "Unexpected USER $username"

            # Do not allow a non-standard user to connect for too long to avoid
            # wasting their balance.
            if [[ $(py "$time > $TIME_LIMIT") == True ]]; then
                WARNING "$username is online for more than $TIME_LIMIT mins. \
                    Try to reconnect..."
                reconnect
            else
                break
            fi
        else
            break
        fi
    fi
done
