import os
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re
import time

errors = []
bit_rates = []
missing_packets = []
transmission_time = []


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
        file_content = [[x[i] for i in range(6, len(x)) if x[i] not in ["GBytes", "MBytes", "KBytes", "Bytes"]] for x in
                        file_content]
        file_content = [[y for y in x] for x in file_content if len(x) > 0]
        file_content = file_content[:len(file_content)]
        # print(file_content, " ", len(file_content))
        return file_content


def parser_error_iperf(file_content, opt):
    error = []
    tmp = 0
    labels = ['Time (s)', 'Error Rate (%)']
    title = 'Error Rate vs Time at ' + opt.role + ' side '

    for x in file_content:
        e = (float(x[4].split('/')[0]) / float(x[5])) * 100
        tmp += e
        error.append(e)

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
    transmission_time.append(len(bit_rate))
    print("Transmission time: ",len(bit_rate))
    bit_rates.append(tmp / len(bit_rate))
    print("Bit Rate Average: ", tmp / len(bit_rate))
    # plotting(bit_rate, opt.simulation_time, labels, title)


def parse_udptetrys(output_file, opt):
    with open(output_file) as f:
        file_content = f.read()
        print("Content")
        file_content = file_content.split('\n')[1::]
        file_content = list(map(lambda x: x.split(r' '), file_content))
        file_content = [[y for y in x if y != ''] for x in file_content]

        if opt.role == 'client':
            n = 11
        elif opt.role == 'server':
            n = 9

        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        file_content = [
            [ansi_escape.sub('', x[i]) for i in range(0, len(x))] for x in file_content if len(x) == n]

        # print(file_content, " ", len(file_content))
        return file_content


def parser_bit_rate_udptetrys(file_content, opt):
    bit_rate = []
    tmp = 0
    labels = ['Time (s)', 'Bit Rate (Mbits/s)']
    title = 'Bit Rate vs Time at ' + opt.role + ' side '

    for x in file_content:
        if x[1] != "inf":
            tmp += float(x[1])
            bit_rate.append(float(x[1]))

    transmission_time.append(len(bit_rate))
    print("Transmission time: ",len(bit_rate))
    bit_rates.append(tmp / len(bit_rate))
    print("Bit Rate Average: ", tmp / len(bit_rate))
    # plotting(bit_rate, len(bit_rate), labels, title)


def parser_error_udptetrys(file_content, opt):
    error = []
    tmp = 0
    labels = ['Time (s)', 'Error Rate (%)']
    title = 'Error Rate vs Time at ' + opt.role + ' side '

    for x in file_content:
        tmp += float(x[3])
    

    errors.append(float(file_content[-1][6])/tmp*100)
    print("Error Average: ", float(file_content[-1][6])/tmp*100)
    # plotting(error, len(error), labels, title)


def parser_missing_udptetrys(file_content, opt):
    missing = []
    tmp = 0
    labels = ['Time (s)', 'Missing Packets']
    title = 'Missing Packets vs Time at ' + opt.role + ' side '

    if opt.role == "server":
        n = 6
    elif opt.role == "client":
        n = 9

    for x in file_content:
        tmp += float(x[n])
        missing.append(float(x[n]))

    missing_packets.append(tmp / len(missing))
    print("Missing Average: ", tmp / len(missing))
    # plotting_stem(missing, len(missing), labels, title)


def plotting(y, x, labels, title):
    t = np.arange(0.0, x + 1, 1)
    y.insert(0, 0.0)

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
        # python3 ./parser.py --role client --tool iperf --protocol udp --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --bytes 100000
        ## TCP
        # python3 ./parser.py --role client --tool iperf --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --bytes 100000
        m = client_interface(opt.ip_address)

        os.system(f"tc qdisc add dev {m} root netem delay {opt.delay_channel}ms loss {opt.packet_loss_rate}%")
        if opt.protocol == "udp":
            command =f"iperf -c {opt.ip_address} -u -i 1 -b {opt.bit_rate}Mb -n {opt.number_bytes}"
        else:
            command =f"iperf -c {opt.ip_address} -i 1 -b {opt.bit_rate}Mb -n {opt.number_bytes}"

        print("Command Client: ",command)
        print("--------------------------------------------")
        os.system(f"{command} | tee ./tmp_client.txt")
        time.sleep(3.0)
        os.system("killall -9 iperf")
        os.system(f"tc qdisc delete dev {m} root netem")

        file_content = parse_iperf("./tmp_client.txt", opt)
        parser_bit_rate_iperf(file_content, opt)


    elif opt.role == "server" and opt.tool == "iperf":
        ## UDP
        # python3 ./parser.py --role server --tool iperf  --protocol udp
        ## TCP
        # python3 ./parser.py --role server --tool iperf
        os.system("killall -9 iperf")
        if opt.protocol == "udp":
            command =f"iperf -s -u -i 1"
            
        else:
            command =f"iperf -s -i 1"

        print("Command Server: ",command)
        print("--------------------------------------------")
        os.system(f"{command} | tee ./tmp_server.txt")
        file_content = parse_iperf("./tmp_server.txt", opt)
        parser_bit_rate_iperf(file_content, opt)
        if opt.protocol == "udp":
            parser_error_iperf(file_content, opt)
        

    elif opt.tool == "ping":
        # python3 ./parser.py --tool ping --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --count 1000
        m = client_interface(opt.ip_address)

        shell_file = "./" + opt.tool + "_" + opt.role + ".sh -d" + str(opt.delay_channel) + " -l " + str(
            opt.packet_loss_rate) + " -a " + opt.ip_address + " -m " + m + " -c " + str(opt.count_icmp_packets)
        print(str(opt.count_icmp_packets))
        simulation(shell_file, opt)

    elif opt.role == "client" and opt.tool == "udptetrys":
        # python3 ./parser.py --role client --tool udptetrys --delay 100 --loss 3 --ip 10.0.0.2 --rate 2 --time 60
        print("udptetrys client")
        opt.protocol = "udp"
        m = client_interface(opt.ip_address)
        number_packets = int(opt.number_bytes/1408)
        delay_udp = (1400*8)/(opt.bit_rate*1000) # in miliseconds


        os.system(f"tc qdisc add dev {m} root netem delay {opt.delay_channel}ms loss {opt.packet_loss_rate}%")
        command =f"./udptetrys -c {opt.ip_address} -d {delay_udp} -b 1 -z 10 -k 5 -n {number_packets}"
        print("Command Client: ",command)
        print("--------------------------------------------")
        os.system(f"{command} | tee ./tmp_client.txt")
        time.sleep(3.0)
        os.system("killall -9 udptetrys")
        os.system(f"tc qdisc delete dev {m} root netem")

        file_content = parse_udptetrys("tmp_client.txt", opt)
        parser_bit_rate_udptetrys(file_content, opt)
        parser_missing_udptetrys(file_content, opt)

    elif opt.role == "server" and opt.tool == "udptetrys":
        # python3 ./parser.py --role server --tool udptetrys
        print("udptetrys server")
        opt.protocol = "udp"
        os.system("killall -9 udptetrys")
        a = "./udptetrys -s"
        print("Command Server: ",a)
        print("--------------------------------------------")
        os.system("./udptetrys -s | tee ./tmp_server.txt")
        file_content = parse_udptetrys("tmp_server.txt", opt)
        parser_bit_rate_udptetrys(file_content, opt)
        parser_missing_udptetrys(file_content, opt)
        parser_error_udptetrys(file_content, opt)


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
ap.add_argument("--bytes", action="store", dest="number_bytes", type=int, default=5000000,
                help="Number of bytes sent by the client")
ap.add_argument("--count", action="store", dest="count_icmp_packets", type=int, default=100,
                help="Count of icmp packets to send")
opt = ap.parse_args()

# ------------------------------------------------------
loss_range = [1]#[1, 2, 5]          # en pourcentage
debit_range = [1, 5, 10]        # en Mbps
delay_range = [100, 200, 500]   # en ms


for loss in loss_range:
    for debit in debit_range:
        for delay in delay_range:
            opt.bit_rate = debit
            opt.packet_loss_rate = loss
            opt.delay_channel = delay
            print("#############################################")
            print("Protocol: ",opt.protocol,"  Loss",opt.packet_loss_rate,"    Bit Rate", opt.bit_rate,"   Delay", opt.delay_channel)
            chose_role(opt)



filename = opt.role+"_"+opt.tool+"_"+opt.protocol+".txt"
f = open(filename, 'w')

# print(bit_rates)
f.write("########## Bit Rate ##########\n")
i = 0
for loss in loss_range:
    f.write(f"---------- Loss: {loss}% -------------\n")
    for debit in debit_range:
        if debit == debit_range[0]:
            f.write(f"Delay [ms]\t\t{delay_range[0]}\t{delay_range[1]}\t{delay_range[2]}\n")
            f.write("Bit rate [Mbps]\n")
        f.write(f"{debit}\t\t\t{bit_rates[i]:.3f}\t{bit_rates[i+1]:.3f}\t{bit_rates[i+2]:.3f}\n")
        i+=3
    f.write("\n")

# print(transmission_time)
f.write("########## Transmission Time ##########\n")
i = 0
for loss in loss_range:
    f.write(f"---------- Loss: {loss}% -------------\n")
    for debit in debit_range:
        if debit == debit_range[0]:
            f.write(f"Delay [ms]\t\t{delay_range[0]}\t{delay_range[1]}\t{delay_range[2]}\n")
            f.write("Bit rate [Mbps]\n")
        f.write(f"{debit}\t\t\t{transmission_time[i]:.3f}\t{transmission_time[i+1]:.3f}\t{transmission_time[i+2]:.3f}\n")
        i+=3
    f.write("\n")


if opt.role == "server" and (opt.protocol == "udp" or opt.tool == "udptetrys"):
    # print(errors)
    f.write("########## Packet Loss Rate ##########\n")
    i = 0
    for loss in loss_range:
        f.write(f"---------- Loss: {loss}% -------------\n")
        for debit in debit_range:
            if debit == debit_range[0]:
                f.write(f"Delay [ms]\t\t{delay_range[0]}\t{delay_range[1]}\t{delay_range[2]}\n")
                f.write("Bit rate [Mbps]\n")
            f.write(f"{debit}\t\t\t{errors[i]:.3f}\t{errors[i+1]:.3f}\t{errors[i+2]:.3f}\n")
            i+=3
        f.write("\n")
        

i = 0

if opt.tool == "udptetrys":
    # print(missing_packets)
    f.write("########## Missing Packets ##########\n")
    i = 0
    for loss in loss_range:
        f.write(f"---------- Loss: {loss}% -------------\n")
        for debit in debit_range:
            if debit == debit_range[0]:
                f.write(f"Delay [ms]\t\t{delay_range[0]}\t{delay_range[1]}\t{delay_range[2]}\n")
                f.write("Bit rate [Mbps]\n")
            f.write(f"{debit}\t\t\t{missing_packets[i]:.3f}\t{missing_packets[i+1]:.3f}\t{missing_packets[i+2]:.3f}\n")
            i+=3
        f.write("\n")





