import os
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def simulation(shell_file, opt):
    os.system(shell_file)
    output_file = opt.tool + "_" + opt.role + ".txt"
    file_content = parser(output_file)
    parser_bit_rate(file_content, opt)
    if opt.role == "server":
        parser_error(file_content, opt)


def parser(output_file):
    with open(output_file) as f:
        file_content = f.read()
        print("Content")
        file_content = file_content.split('\n')[1::]
        file_content = list(map(lambda x: x.split(r' '), file_content))
        file_content = [[y for y in x if y != ''] for x in file_content]
        file_content = [
            [x[i] for i in range(0, len(x)) if len(x) >= 8 and x[i] != "out-of-order" and x[i] != "received"] for x in
            file_content[6:]]  # 10 simulation time
        file_content = [[x[i] for i in range(0, len(x)) if i > 5 and x[i] != "KBytes"] for x in file_content]
        file_content = [[y for y in x] for x in file_content if len(x) > 0]
        file_content = file_content[:opt.simulation_time]
        print(file_content, " ", len(file_content))
        return file_content


def parser_error(file_content, opt):
    error = []
    tmp = 0
    label = 'Error Rate (%)'
    title = 'Error Rate vs Time at ' + opt.role + ' side '

    for x in file_content:
        tmp += float(x[4].split('/')[0]) / float(x[5])
        error.append(float(x[4].split('/')[0]) / float(x[5]))

    print("Error Average: ", tmp / opt.simulation_time)
    plotting(error, opt.simulation_time, label, title)


def parser_bit_rate(file_content, opt):
    bit_rate = []
    tmp = 0
    label = 'Bit Rate (Mbits/sec)'
    title = 'Bit Rate vs Time at ' + opt.role + ' side '

    for x in file_content:
        if x[1] == "Kbits/sec":
            tmp += float(x[0]) / 1000
            bit_rate.append(float(x[0]) / 1000)
        elif x[1] == "Mbits/sec":
            tmp += float(x[0])
            bit_rate.append(float(x[0]))
        elif x[1] == "Gbits/sec" and float(x[0]) < 1:
            tmp += float(x[0]) * 1000
            bit_rate.append(float(x[0]) * 1000)

    print("Bit Rate Average: ", tmp / opt.simulation_time)

    plotting(bit_rate, opt.simulation_time, label, title)


def plotting(y, x, label, title):
    t = np.arange(1.0, x + 1, 1)

    fig, ax = plt.subplots()
    ax.plot(t, y)

    ax.set(xlabel='time (s)', ylabel=label,
           title=title)
    ax.grid()

    fig.savefig("test.png")
    plt.show()


# -----------------------------------------------------------------------------------
# for param in sys.argv:
#     print(param)

ap = argparse.ArgumentParser(description="a SCHC simulator.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--role", action="store", dest="role", default="client", help="specify a role: client or server.")
ap.add_argument("--tool", action="store", dest="tool", default="iperf", help="Traffic tool: iperf or udptetrys")
ap.add_argument("--protocol", action="store", dest="protocol", default="udp", help="Protocol: udp or tcp")
ap.add_argument("--delay", action="store", dest="delay_channel", type=int, default=100, help="Delay channel in ms.")
ap.add_argument("--loss", action="store", dest="packet_loss_rate", type=int, default=3,
                help="Packet loss rate in percentage.")
ap.add_argument("--ip", action="store", dest="ip_address", default="", help="IP address")
ap.add_argument("--rate", action="store", dest="bit_rate", type=int, default=2, help="Bit rate in Mbps")
ap.add_argument("--time", action="store", dest="simulation_time", type=int, default=70,
                help="Simulation time in seconds")

opt = ap.parse_args()

# ------------------------------------------------------

if opt.role == "client" and opt.tool == "iperf":
    # python3 ./parser.py --role client --tool iperf --protocol udp --delay 100 --loss 3 --ip 10.0.0.1 --rate 2 --time 60
    shell_file = "./" + opt.tool + "_" + opt.role + ".sh -d " + str(opt.delay_channel) + " -l " + str(
        opt.packet_loss_rate) + " -a " + opt.ip_address + " -b " + str(opt.bit_rate) + " -t " + str(opt.simulation_time)
    simulation(shell_file, opt)

elif opt.role == "server" and opt.tool == "iperf":
    # python3 ./parser.py --role server --tool iperf --time 60
    shell_file = "./" + opt.tool + "_" + opt.role + ".sh -t" + str(opt.simulation_time + 10)
    simulation(shell_file, opt)
