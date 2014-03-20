#!/bin/bash

# first kill any other copies of the script

./monitor_processor_stop.sh

# now restart the loop

nohup ./monitor_processor_loop.sh > ../logs/monitor_processor_loop.out 2>&1 &
