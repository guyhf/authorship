#!/bin/bash

# first kill any other copies of the script

PROCESS="./monitor_webapp_loop.sh"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  kill -9 $PIDS
fi

