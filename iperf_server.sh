#!/bin/bash

iperf -s -u -i 1 -t 30 | tee iperf_server.txt
