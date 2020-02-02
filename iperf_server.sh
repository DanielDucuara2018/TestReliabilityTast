#!/bin/bash

while getopts t: option; do
	case "${option}"
	in
  t) SIMULATION_TIME=${OPTARG};;
	esac
done

echo $SIMULATION_TIME

iperf -s -u -i 1 -t $SIMULATION_TIME | tee iperf_server.txt
