#!/bin/bash

while getopts d:l:a:m:c: option; do
	case "${option}"
	in
	d) DELAY_CHANNEL_FORWARD=${OPTARG};;
	l) PACKET_LOSS_RATE=${OPTARG};;
	a) SERVER_ADDRESS=${OPTARG};;
  m) TERIMAL=${OPTARG};;
  c) COUNT=${OPTARG};;
	esac
done

echo $DELAY_CHANNEL_FORWARD"ms"
echo $PACKET_LOSS_RATE
echo $SERVER_ADDRESS
echo $TERIMAL
echo $COUNT

tc qdisc add dev $TERIMAL root netem delay $DELAY_CHANNEL_FORWARD"ms" loss $PACKET_LOSS_RATE"%"
ping -i 0.01 -c $COUNT $SERVER_ADDRESS | tee ping_client.txt
tc qdisc delete dev $TERIMAL root netem