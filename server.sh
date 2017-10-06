#!/bin/bash
if [ ! -n "$1" ]
then
    echo "Usages: sh server.sh [start|stop|restart|status|log]"
    exit 0
fi

if [ $1 = start ]
then
    psid=`ps aux | grep "python" | grep "heatbox.py" | grep -v "grep" | wc -l`
    if [ $psid -gt 0 ]
    then
        echo "Heatbox is running!"
        exit 0
    else
        nohup python heatbox.py > heatbox.log 2>&1 &
        echo "Start heatbox service [OK]"
    fi

elif [ $1 = stop ];then
    ps -ef | grep "heatbox.py" | grep -v grep | cut -c 10-15 | xargs kill -9
    echo "Stop heatbox service [OK]"

elif [ $1 = restart ];then
    ps -ef | grep "heatbox.py" | grep -v grep | cut -c 10-15 | xargs kill -9
    echo "Stop heatbox service [OK]"
    sleep 2
    nohup python heatbox.py > heatbox.log 2>&1 &
    echo "Start heatbox service [OK]"

elif [ $1 = status ];then
    ps -ef | grep "heatbox.py" | grep -v grep

elif [ $1 = log ];then
    tail -f heatbox.log

else
    echo "Usages: sh server.sh [start|stop|restart|status|log]"
fi
