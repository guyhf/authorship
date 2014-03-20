#!/bin/bash

# first kill any other copies of this script

PROCESS="./processor_loop.sh"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  echo Killing $PROCESS pid=$PIDS
  kill -9 $PIDS
fi

PROCESS="./processor.py"

PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`

if [ ! -z "$PIDS" ]; then
  echo Killing $PROCESS pid=$PIDS
  kill -9 $PIDS
fi