import os
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re
import time

errors = []
bit_rates = []

def simulation(shell_file, opt):
    os.system(shell_file)
    output_file = opt.tool + "_" + opt.role + ".txt"
    if opt.tool == "iperf":
        file_content = parse_iperf(output_file, opt)
        parser_bit_rate_iperf(file_content, opt)
        if opt.role == "server" and opt.protocol == "udp":
            parser_error_iperf(file_content, opt)
    elif opt.tool == "ping":
        file_content = parse_ping(output_file)
        parser_icmp_sequence_ping(file_content, opt)


def parse_ping(output_file):
    with open(output_file) as f:
        file_content = f.read()
        print("Content")
        file_content = file_content.split('\n')[1::]
        file_content = list(map(lambda x: x.split(r' '), file_content))
        file_content = [[y for y in x] for x in file_content if len(x) == 8]

        # print(file_content)
        return file_content


def parser_icmp_sequence_ping(file_content, opt):
    sequence = np.ones((opt.count_icmp_packets,), dtype=int)
    labels = ['State', 'Sequence Number']
    title = 'Packet State at ' + opt.role + ' side '

    for x in file_content:
        sequence_number = int(x[4].split('=')[1]) - 1
        # print(sequence_number)
        sequence[sequence_number] = 0

    plotting_stem(sequence, len(sequence), labels, title)


def parse_iperf(output_file, opt):
    with open(output_file) as f:
        file_content = f.read()
        print("Content")
        file_content = file_content.split('\n')[1::]
        file_content = list(map(lambda x: x.split(r' '), file_content))
        file_content = [[y for y in x if y != ''] for x in file_content]
        n = 0
        if opt.protocol == "udp":
            n = 6
        else:
            n = 5
        file_content = [
            [x[i] for i in range(0, len(x)) if x[i] not in ["out-of-order", "received"]] for x in
            file_content[n:] if len(x) >= 8]
        file_content = [[x[i] for i in range(6, len(x)) if x[i] not in ["GBytes", "MBytes", "KBytes", "Bytes"]]for x in file_content]
        file_content = [[y for y in x] for x in file_content if len(x) > 0]
        file_content = file_content[:opt.simulation_time]
        # print(file_content, " ", len(file_content))
        return file_content

def parse_udptetrys(output_file, opt):
    with open(output_file) as f:
        file_content = f.read()
        print("Content")
        file_content = file_content.split('\n')[1::]
        file_content = list(map(lambda x: x.split(r' '), file_content))
        file_content = [[y for y in x if y != ''] for x in file_content]
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        file_content = [
            [ansi_escape.sub('', x[i]) for i in range(0, len(x))] for x in file_content if len(x) == 11]
        # file_content = [[x[i].split('\x')[0] for i in range(0, len(x)) if i in [0,1,2,3,4,7,9]]for x in file_content]
        # file_content = [[y for y in x] for x in file_content if len(x) > 0]
        # file_content = file_content[:opt.simulation_time]
        
        print(file_content, " ", len(file_content))
        # return file_content


def parser_error_iperf(file_content, opt):
    error = []
    tmp = 0
    labels = ['Time (s)', 'Error Rate (%)']
    title = 'Error Rate vs Time at ' + opt.role + ' side '

    for x in file_content[:-1]:
        tmp += float(x[4].split('/')[0]) / float(x[5])
        error.append(float(x[4].split('/')[0]) / float(x[5]))

    errors.append(tmp / len(error) *100)
    print("Error Average: ", tmp / len(error) *100," %")
    # plotting(error, opt.simulation_time, labels, title)


def parser_bit_rate_iperf(file_content, opt):
    bit_rate = []
    tmp = 0
    labels = ['Time (s)', 'Bit Rate (Mbits/s)']
    title = 'Bit Rate vs Time at ' + opt.role + ' side '

    for x in file_content[:-1]:
        if x[1] == "bits/sec":
            tmp += float(x[0]) / 10e6
            bit_rate.append(float(x[0]) / 10e6)
        if x[1] == "Kbits/sec":
            tmp += float(x[0]) / 1000
            bit_rate.append(float(x[0]) / 1000)
        elif x[1] == "Mbits/sec":
            tmp += float(x[0])
            bit_rate.append(float(x[0]))
        elif x[1] == "Gbits/sec" and float(x[0]) < 1:
            tmp += float(x[0]) * 1000
            bit_rate.append(float(x[0]) * 1000)

    bit_rates.append(tmp / len(bit_rate))
    print("Bit Rate Average: ", tmp / len(bit_rate))
    # plotting(bit_rate, opt.simulation_time, labels, title)


def plotting(y, x, labels, title):
    t = np.arange(0.0, x + 1, 1)
    y.insert(0,0.0)

    fig, ax = plt.subplots()
    ax.plot(t, y)

    ax.set(xlabel=labels[0], ylabel=labels[1],
           title=title)
    ax.grid()

    fig.savefig("test.png")
    plt.show()


def plotting_stem(y, x, labels, title):
    t = np.arange(1.0, x + 1, 1)

    fig, ax = plt.subplots()
    ax.stem(t, y)

    ax.set(xlabel=labels[0], ylabel=labels[1],
           title=title)
    ax.grid()

    fig.savefig("test2.png")
    plt.show()


def client_interface(ip_address):
    if ip_address == "10.0.0.1":  # server ip address
        m = "h2-eth0"  # client interface
    elif ip_address == "10.0.0.2":  # server ip address
        m = "h1-eth0"  # client interface
    return m



def chose_role(opt):
    if opt.role == "client" and opt.tool == "iperf":
        ## UDP
        # python3 ./parser.py --role client --tool iperf --protocol udp --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --time 60
        ## TCP
        # python3 ./parser.py --role client --tool iperf --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --time 60
        m = client_interface(opt.ip_address)

        shell_file = "./" + opt.tool + "_" + opt.role + ".sh -d " + str(opt.delay_channel) + " -l " + str(
            opt.packet_loss_rate) + " -a " + opt.ip_address + " -b " + str(opt.bit_rate) + " -t " + str(
            opt.simulation_time) + " -m " + m + " -p " + opt.protocol

        simulation(shell_file, opt)
        os.system("killall -9 iperf")

    elif opt.role == "server" and opt.tool == "iperf":
        ## UDP
        # python3 ./parser.py --role server --tool iperf  --protocol udp --time 60
        ## TCP
        # python3 ./parser.py --role server --tool iperf  --time 60
        # shell_file = "./" + opt.tool + "_" + opt.role + ".sh -t" + str(opt.simulation_time +1) + " -p " + opt.protocol
        shell_file = "./" + opt.tool + "_" + opt.role + ".sh -p " + opt.protocol
        simulation(shell_file, opt)

    elif opt.tool == "ping":
        # python3 ./parser.py --tool ping --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --count 1000
        m = client_interface(opt.ip_address)

        shell_file = "./" + opt.tool + "_" + opt.role + ".sh -d" + str(opt.delay_channel) + " -l " + str(
            opt.packet_loss_rate) + " -a " + opt.ip_address + " -m " + m + " -c " + str(opt.count_icmp_packets)
        print(str(opt.count_icmp_packets))
        simulation(shell_file, opt)

    elif opt.role == "client" and opt.tool == "udptetrys":
        # python3 ./parser.py --role client --tool udptetrys --delay 100 --loss 3 --ip 10.0.0.2 --rate 2 --time 60
        m = client_interface(opt.ip_address)
        delay_tetrys = 1400*8/(opt.bit_rate*1000)
        os.system(f"tc qdisc add dev {m} root netem delay {opt.delay_channel}ms loss {opt.packet_loss_rate}%")
        os.system(f"./udptetrys -c {opt.ip_address} -d {delay_tetrys} -b 1 -z 10 -k 5 -n 2000 | tee ./udptetrys_client.txt")
        # os.system("killall -9 udptetrys")
        os.system(f"tc qdisc delete dev {m} root netem")   
        print("Client.txt done!!!!")
        parse_udptetrys("udptetrys_client.txt",opt)

    elif opt.role == "server" and opt.tool == "udptetrys":
        # python3 ./parser.py --role server --tool udptetrys
        print("udptetrys server")
        os.system(f"./udptetrys -s | tee ./udptetrys_server.txt")


# -----------------------------------------------------------------------------------
# for param in sys.argv:
#     print(param)

ap = argparse.ArgumentParser(description="a SCHC simulator.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--role", action="store", dest="role", default="client", help="specify a role: client or server.")
ap.add_argument("--tool", action="store", dest="tool", default="iperf", help="Traffic tool: iperf or udptetrys")
ap.add_argument("--protocol", action="store", dest="protocol", default="tcp", help="Protocol: udp or tcp")
ap.add_argument("--delay", action="store", dest="delay_channel", type=int, default=100, help="Delay channel in ms.")
ap.add_argument("--loss", action="store", dest="packet_loss_rate", type=int, default=3,
                help="Packet loss rate in percentage.")
ap.add_argument("--ip", action="store", dest="ip_address", default="", help="IP address")
ap.add_argument("--rate", action="store", dest="bit_rate", type=int, default=2, help="Bit rate in Mbps")
ap.add_argument("--time", action="store", dest="simulation_time", type=int, default=70,
                help="Simulation time in seconds")
ap.add_argument("--count", action="store", dest="count_icmp_packets", type=int, default=100,
                help="Count of icmp packets to send")
opt = ap.parse_args()

# ------------------------------------------------------

for loss in [1, 2, 5]:
    for debit in [1, 5, 10]:
        for delay in [100, 200, 500]:
            opt.bit_rate = debit
            opt.packet_loss_rate = loss
            opt.delay_channel = delay

            print (opt.protocol," Bit Rate", opt.bit_rate,"  Loss",opt.packet_loss_rate, "   Delay", opt.delay_channel)
            chose_role(opt)

filename = opt.role+"_"+opt.tool+".txt"
f = open(filename, 'w')
f.write("hello\talex")

if opt.role == "server" and opt.protocol == "udp":
    print(errors)
    i = 0
    for loss in [1, 2, 5]:
        print(f"Loss: {loss}")
        for debit in [1, 5, 10]:
            if debit == 1:
                print("Delay [ms]\t\t100\t200\t500")
                print("Bit rate [Mbps]")
            print(f"{debit}\t\t\t{errors[i]:.3f}\t{errors[i+1]:.3f}\t{errors[i+2]:.3f}")
            i+=3
        print()
        

print(bit_rates)

i = 0
for loss in [1, 2, 5]:
    print(f"Loss: {loss}")
    for debit in [1, 5, 10]:
        if debit == 1:
            print("Delay [ms]\t\t100\t200\t500")
            print("Bit rate [Mbps]")
        print(f"{debit}\t\t\t{bit_rates[i]:.3f}\t{bit_rates[i+1]:.3f}\t{bit_rates[i+2]:.3f}")
        i+=3
    print()