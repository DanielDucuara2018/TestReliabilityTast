#!/bin/bash

while getopts d:l:a:b: option; do
	case "${option}"
	in
	d) DELAY_CHANNEL_FORWARD=${OPTARG};;
	l) PACKET_LOSS_RATE=${OPTARG};;
	a) SERVER_ADDRESS=${OPTARG};;
	b) BIT_RATE=${OPTARG};;
	esac
done

echo $DELAY_CHANNEL_FORWARD"ms"
echo $PACKET_LOSS_RATE
echo $SERVER_ADDRESS
echo $BIT_RATE

tc qdisc add dev h2-eth0 root netem delay $DELAY_CHANNEL_FORWARD"ms" loss $PACKET_LOSS_RATE"%"
#ping 10.0.0.1
iperf -c $SERVER_ADDRESS -u -i 1 -t 10 -b $BIT_RATE"Mb" | tee iperf_client.txt
tc qdisc delete dev h2-eth0 root netem
