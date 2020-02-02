#!/bin/bash

while getopts d:l:a:b:t:m:p: option; do
	case "${option}"
	in
	d) DELAY_CHANNEL_FORWARD=${OPTARG};;
	l) PACKET_LOSS_RATE=${OPTARG};;
	a) SERVER_ADDRESS=${OPTARG};;
	b) BIT_RATE=${OPTARG};;
  t) SIMULATION_TIME=${OPTARG};;
  m) TERIMAL=${OPTARG};;
  p) PROTOCOL=${OPTARG};;
	esac
done

echo $DELAY_CHANNEL_FORWARD"ms"
echo $PACKET_LOSS_RATE
echo $SERVER_ADDRESS
echo $BIT_RATE
echo $SIMULATION_TIME
echo $TERIMAL
echo $PROTOCOL

tc qdisc add dev $TERIMAL root netem delay $DELAY_CHANNEL_FORWARD"ms" loss $PACKET_LOSS_RATE"%"
#ping 10.0.0.1
if [ $PROTOCOL = "udp" ]
then
  iperf -c $SERVER_ADDRESS -u -i 1 -t $SIMULATION_TIME -b $BIT_RATE"Mb" | tee iperf_client.txt
else
  iperf -c $SERVER_ADDRESS -i 1 -t $SIMULATION_TIME -b $BIT_RATE"Mb" | tee iperf_client.txt
fi

tc qdisc delete dev $TERIMAL root netem
