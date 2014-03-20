#!/bin/bash
PROCESS="./webapp.py"

SERVER_BASE=`cat config.ini | awk '/server.baseURL/ {print}' | sed 's/.*"\(.*\)"/\1/'`
while true
	do
		STATUS=`curl -s ${SERVER_BASE}/alive`
		if [ "$STATUS" ] ; then
			if [ "$STATUS" != "OK" ]; then
				PIDS=`ps auxw|grep $PROCESS |grep -v grep|awk '{print $2}'`
				if [ ! -z "$PIDS" ]; then
			  		echo Killing $PROCESS pid=$PIDS
			  		kill -9 $PIDS
				fi
			fi

			# it will restart on its own (webapp_loop.sh will restart it)
		fi
		sleep 3
	done
