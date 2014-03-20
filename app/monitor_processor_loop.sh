#!/bin/bash

while true
	do
		/Library/Server/Web/Data/WebApps/authorship/bin/python ./monitor_processor.py
		sleep 1
	done
