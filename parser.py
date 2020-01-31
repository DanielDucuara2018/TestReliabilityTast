import os
import argparse

# -----------------------------------------------------------------------------------
# for param in sys.argv:
#     print(param)

ap = argparse.ArgumentParser(description="a SCHC simulator.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--role", action="store", dest="role", default="client", help="specify a role: client or server.")
ap.add_argument("--tool", action="store", dest="tool", default="iperf", help="Traffic tool: iperf or udptetrys")
ap.add_argument("--protocol", action="store", dest="protocol", default="udp", help="Protocol: udp or tcp")
ap.add_argument("--delay", action="store", dest="delay_channel", type=int, default=100, help="Delay channel in ms.")
ap.add_argument("--loss", action="store", dest="packet_loss_rate", type=int, default=3, help="Packet loss rate in percentage.")
ap.add_argument("--ip", action="store", dest="ip_address", default="", help="IP address")
ap.add_argument("--rate", action="store", dest="bit_rate", type=int, default=2, help="Bit rate in Mbps")
opt = ap.parse_args()
# ------------------------------------------------------

if opt.role == "client" and opt.tool == "iperf":
    # python3 ./parser.py --role client --tool iperf --protocol udp --delay 100 --loss 3 --ip 10.0.0.1 --rate 2
    file = "./" + opt.tool + "_" + opt.role + ".sh -d " + str(opt.delay_channel) + " -l " + str(opt.packet_loss_rate) + " -a " + opt.ip_address + " -b " + str(opt.bit_rate)
    print(file)
    os.system(file)
elif opt.role == "server" and opt.tool == "iperf":
    # python3 ./parser.py --role server --tool iperf
    file = "./" + opt.tool + "_" + opt.role + ".sh"
    print(file)
    os.system(file)
