#!/bin/bash

# first kill any other copies of the script

PROCESS="./webapp_loop.sh"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  echo Killing $PROCESS pid=$PIDS
  kill -9 $PIDS
fi

# now kill any webapp.py processes

PROCESS="./webapp.py"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  kill -9 $PIDS
fi

