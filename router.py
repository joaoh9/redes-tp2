import sys
import threading
import json
import re
import socket
from colorama import Fore

PORT = 55151

routes = {}


def add_link(receiver, distance):
    if receiver not in routes:
        routes[receiver] = [[receiver, distance]]
    else:
        for i in range(len(routes[receiver])):
            if receiver == routes[receiver][i][0]:
                print("Route " + receiver + " already added.")
                return
        routes[receiver].append[[receiver, distance]]
    print("Added route to " + receiver + " with distance " + str(distance))


def del_link(enlace):
    # ip = enlace[1]
    # ....
    print("Del enlace")


def get_destination(destination):
    return routes[destination][0][0]


def create_data_packet(destination, messsage):
    return {
        "type": "data",
        "source": ADDR,
        "destination": destination,
        "payload": messsage
    }


def send_packet(packet):
    destination = packet['destination']
    json_packet = json.dumps(packet)
    message = bytes(json_packet, 'utf-8')
    SOCK.sendto(message, (destination, PORT))


def prompt():
    while 1:
        s = input()
        cmd = s.split()
        if len(cmd) is 0:
            continue
        elif cmd[0] == "add":
            add_link(cmd[1], int(cmd[2]))
        elif cmd[0] == "del":
            del_link(cmd[1])
            print("Run del")
        elif cmd[0] == "trace":
            print("Run trace")
        elif cmd[0] == "status":
            # print(json.dumps(routes, sort_keys=True, indent=4))
            output = json.dumps(routes, sort_keys=True, indent=4)
            output2 = re.sub(r'": \[\s+', '": [', output)
            output3 = re.sub(r'",\s+', '", ', output2)
            output4 = re.sub(r'"\s+\]', '"]', output3)
            print(Fore.RED + output4)
        elif cmd[0] == "msg":
            if len(cmd) < 2:
                print("Too few arguments for msg")
                continue
            receiver = cmd[1]
            message = cmd[2]
            packet = create_data_packet(receiver, message)
            send_packet(packet)
        elif cmd[0] == "help":
            print("add del trace data help quit")
        elif cmd[0] == "quit":
            break
        else:
            print("Command not found")


def recv_package():
    while True:
        msg, ip = SOCK.recvfrom(1024)
        if len(msg) > 0:
            msg = bytes.decode(msg)
            message = json.loads(msg)
            treat_package(message)


def treat_package(message):
    if message['type'] == "data":
        print ('data')
    if message['type'] == "trace":
        print ('trace')
    if message['type'] == "update":
        print ('update')


def read_file(startup_file):
    print('read file')


def main():

    global SOCK
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SOCK.bind((sys.argv[1], PORT))

    global ADDR
    ADDR = sys.argv[1]
    print("Address: " + ADDR)

    period = int(sys.argv[2])
    print("Period: " + str(period))
    
    # --startup-comands
    if len(sys.argv) > 3:
        startup = sys.argv[3]
        startup_file = open(startup, "r")
        read_file(startup_file)

    t_listen = threading.Thread(target=recv_package)
    t_listen.start()
    
    t_prompt = threading.Thread(target=prompt)
    t_prompt.start()

    t_prompt.join()
    

if __name__ == "__main__":
    main()
