#!/bin/bash

# first kill any other copies of this script

./processor_stop.sh

# now restart it

nohup ./processor_loop.sh > ../logs/processor_loop.out 2>&1 &
