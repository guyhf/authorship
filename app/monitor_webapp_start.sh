#!/bin/bash

# first kill any other copies of the script

./monitor_webapp_stop.sh

# now restart the loop

nohup ./monitor_webapp_loop.sh > ../logs/monitor_webapp_loop.out 2>&1 &
