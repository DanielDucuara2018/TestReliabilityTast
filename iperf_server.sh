#!/bin/bash

while getopts t:p: option; do
	case "${option}"
	in
  t) SIMULATION_TIME=${OPTARG};;
  p) PROTOCOL=${OPTARG};;
	esac
done

echo $SIMULATION_TIME
echo $PROTOCOL

if [ $PROTOCOL = "udp" ]
then
  iperf -s -u -i 1 -t $SIMULATION_TIME | tee iperf_server.txt
else
  iperf -s -i 1 -t $SIMULATION_TIME | tee iperf_server.txt
fi