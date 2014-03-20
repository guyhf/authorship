#!/bin/bash

Start ()
{
	echo -n "Starting..."
	./webapp_start.sh
	./monitor_webapp_start.sh
	./processor_start.sh
	./monitor_processor_start.sh
	echo "Done"
}

Stop ()
{
	echo -n "Stoping..."
	./monitor_webapp_stop.sh
	./monitor_processor_stop.sh
	./webapp_stop.sh
	./processor_stop.sh
	rm -f ../sessions/session-*.lock
	echo "Done"
}

Restart ()
{
    Stop
    Start
}

Initialize ()
{
	echo -n "Really initialize? [y/n]: "
	read really1
	
	if [ $really1 == "y" ] ; then
		echo -n "Are you sure?  This will delete EVERYTHING! [y/n]: "
		read really2
		if [ $really2 == "y" ] ; then
			/Library/Server/Web/Data/WebApps/authweb/bin/python ./database_initialize.py drop > /dev/null 2>&1
			/Library/Server/Web/Data/WebApps/authweb/bin/python ./database_initialize.py create > /dev/null 2>&1
			rm -rf files/authweb_*
			rm -f ../sessions/session-*
			rm -f ../logs/*.out
		fi
	fi

}

case "$1" in 
     'start') 
         Start
         ;;
     'stop')
         Stop
         ;;
     'restart')
         Restart
         ;;
     'init')
         Initialize
         ;;
     *)
         echo "Usage: $0 [start|stop|restart|init]" 
         ;;
esac
