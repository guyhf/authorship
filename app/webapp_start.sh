#!/bin/bash

# first kill any other copies of the script

./webapp_stop.sh

# now restart the loop

nohup ./webapp_loop.sh > ../logs/webapp_loop.out 2>&1 &
