### constants
# standard account username and md5
ACCOUNT_FILE=/etc/.auto_connect.cfg

# allow other users to stay for at most TIME_LIMIT mins
# to avoid wasting their balance.
TIME_LIMIT=30

# statistic page URL
URL=https://net.tsinghua.edu.cn/cgi-bin/rad_user_info

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
    echo "`getCurrentTime` $1" >> LOG_FILE
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
    response=$(curl -s --connect-timeout 5 --get $URL)
    # Disconnect or Timeout
    if [ -z $response ]; then
        echo 
    else
        echo $response | awk -F, '{print $1,$2,$3,$7,$9}'
    fi
}

# TODO
# logout from current network, then log in
function reconnect {
    read USERNAME PASSWD <<< cat ACCOUNT_FILE
    echo
}

### main
read UNLIMITED_USERNAME PASSWD <<< cat ACCOUNT_FILE
for try in {1..5}
do
    status=$(getStatus)
    if [ -z $status ]; then
        ERROR "Offline. #$try Try to reconnect..."
        reconnect
    else
        # load status into variables
        read username logintime currenttime usage ip <<< echo $status

        # convert time to min
        time=$(py "round($currenttime-$logintime/60, 3)")

        # convert network usage to GB
        usage=$(py "round($usage/1024/1024/1024, 3)")

        INFO "Online. USERNAME-$username IP-$ip TIME-$time USAGE-$usage"

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
