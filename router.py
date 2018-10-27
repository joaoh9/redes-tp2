import sys
import threading
import json
import re
import socket
from Table import Table

PORT = 55151


def create_data_packet(destination, message):
    """
    Create a dictionary with data in a packet to be send.
    :param destination: Router destination IP address.
    :type destination: str
    :param message: Text message to be sent.
    :type message: str
    :return: Dictionary.
    :rtype: dict
    """
    return {
        "type": "data",
        "source": ADDR,
        "destination": destination,
        "payload": message
    }


def create_update_packet(destination, payload):
    return {
        "type": "update",
        "source": ADDR,
        "destination": destination,
        "payload": payload
    }


def send_packet(packet):
    """
    Send a dict packet to a router.
    :param packet: Dict packet with info.
    :type packet: dict
    """
    destination = table.get_destination_by_routes(packet['destination'])
    json_packet = json.dumps(packet)
    message = bytes(json_packet, 'utf-8')
    SOCK.sendto(message, (destination, PORT))
    print(packet['type'] + ' packet sent')


def prompt():
    """
    Read commands and select the right function.
    """
    while 1:
        s = input()
        cmd = s.split()
        if len(cmd) is 0:
            continue
        elif cmd[0] == "add":
            if len(cmd) < 3:
                print("Too few arguments")
                continue
            table.add_link(cmd[1], int(cmd[2]))
        elif cmd[0] == "del":
            if len(cmd) < 3:
                print("Too few arguments")
                continue
            table.del_link(cmd[1])
        elif cmd[0] == "trace":
            if len(cmd) < 3:
                print("Too few arguments")
                continue
            print("Run trace")
        elif cmd[0] == "status":
            print(table.to_string())
        elif cmd[0] == "msg":
            if len(cmd) < 3:
                print("Too few arguments")
                continue
            receiver = cmd[1]
            message = cmd[2]
            packet = create_data_packet(receiver, message)
            send_packet(packet)
            print("send msg")
        elif cmd[0] == "help":
            print("add del trace data help quit")
        elif cmd[0] == "quit":
            break
        else:
            print("Command not found")


def recv_packet():
    while True:
        msg, ip = SOCK.recvfrom(1024)
        if len(msg) > 0:
            msg = bytes.decode(msg)
            message = json.loads(msg)
            treat_packet(message)


def treat_packet(packet):
    print(packet['type'])


def update(period):
    threading.Timer(period, update, kwargs={'period': period}).start()
    destinations = []
    
    for key in table.routes:
        print(key)
        if table.routes[key].is_link is True:
            destinations.append(key)

    for i in range(len(destinations)):
        payload = {}
        for key in table.routes:
            if key != destinations[i]:
                faster_route = table.routes[key].options[0] # sempre o primeiro indice tem a rota mais curta
                destination = faster_route.destination
                distance = faster_route.distance

                payload[destination] = distance
        update_packet = create_update_packet(destinations[i], payload)
        send_packet(update_packet)


def read_file(startup_file):
    while True:
        line = startup_file.readline().replace("\n", "")
        if len(line) == 0:
            break
        cmd = line.split()
        
        if cmd[0] == "add":
            table.add_link(cmd[1], int(cmd[2]))
            print("router " + cmd[1] + " with distance " + cmd[2] + " added")
        else:
            print('Command is not add command')
    print('Finished reading file')
    return


def main():
    
    global SOCK
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SOCK.bind((sys.argv[1], PORT))

    global ADDR
    ADDR = sys.argv[1]
    print("Address: " + ADDR)

    period = int(sys.argv[2])
    print("Period: " + str(period))

    global table
    table = Table()
    
    # --startup-comands
    if len(sys.argv) > 3:
        startup = sys.argv[3]
        startup_file = open(startup, "r")
        read_file(startup_file)

    t_recv = threading.Thread(target=recv_packet)
    t_recv.start()
    
    t_prompt = threading.Thread(target=prompt)
    t_prompt.start()

    update(period)

    t_prompt.join()
    

if __name__ == "__main__":
    main()
