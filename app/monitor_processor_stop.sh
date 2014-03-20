#!/bin/bash

# first kill any other copies of the script

PROCESS="./monitor_processor_loop.sh"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  echo Killing $PROCESS pid=$PIDS
  kill -9 $PIDS
fi

PROCESS="./monitor_processor.py"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  echo Killing $PROCESS pid=$PIDS
  kill -9 $PIDS
fi