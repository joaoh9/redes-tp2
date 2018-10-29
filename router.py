import sys
import threading
import json
import re
import socket
from Table import Table
import time

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

def treat_data(packet):
    print(packet['payload'])


def create_update_packet(destination, payload):
    return {
        "type": "update",
        "source": ADDR,
        "destination": destination,
        "payload": payload
    }


def treat_update(packet):
    payload = packet['payload']
    source = packet['source']
    #print('update coming fron: ', source)
    #print('update payload: ', payload)
    if source not in table.routes:
        print("There is not " + source + " in table.")
        return

    distance_from_source = table.routes[source].min
    
    # print('got this payload: ' + str(payload) + ' from :' + source)
    for key in payload:
        if key != ADDR:
            table.add_learned_router(key, distance_from_source + int(payload[key]), source)


def get_treater(type):
    treat_function = {
        "data": treat_data,
        "update": treat_update
        #Q"trace": treat_trace
    }
    return treat_function.get(type)


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


def recv_packet():
    while True:
        msg, ip = SOCK.recvfrom(1024)
        if len(msg) > 0:
            msg = bytes.decode(msg)
            packet = json.loads(msg)
            treat_function = get_treater(packet["type"])
            treat_function(packet)


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
            if len(cmd) < 2:
                print("Too few arguments")
                continue
            table.del_link(cmd[1])
        elif cmd[0] == "trace":
            if len(cmd) < 2:
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


def update(period):
    while True:
        destinations = []
        for key in table.routes:
            if table.routes[key].is_link is True:
                destinations.append(key)

        for dest in destinations:
            payload = {}
            for key in table.routes:
                faster_route = table.routes[key].options[0]
                # print(' opt.learned_from: ' + str(faster_route.learned_from) + ' dest: ' + dest)
                # print("Result: " + str(faster_route.learned_from != dest))
                if faster_route.destination != dest and faster_route.learned_from != dest and key != dest:
                    payload[key] = faster_route.distance

            # print('payload: ' + str(payload) + ' to : ' + dest)
            update_packet = create_update_packet(dest, payload)
            send_packet(update_packet)
                        
        # print(table.to_string())
        time.sleep(period)


def read_file(startup_file):
    while True:
        line = startup_file.readline().replace("\n", "")
        if len(line) == 0:
            break
        cmd = line.split()
        
        if cmd[0] == "add":
            table.add_link(cmd[1], int(cmd[2]))
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

    t_update = threading.Thread(target=update, kwargs={'period': period})
    t_update.start()

    t_prompt.join()
    

if __name__ == "__main__":
    main()
