import sys
import threading
import json
import re
import socket
from Table import Table
import time
import argparse


PORT = 55151
MAX_LOOP_SIZE = 20


def read_file(startup_file):
    """
    Read startup file and add links on table.
    :param startup_file:
    :type startup_file: TextIO
    """
    while True:
        line = startup_file.readline().replace("\n", "")
        if len(line) == 0:
            break
        cmd = line.split()
        if cmd[0] == "add":
            table.add_link(cmd[1], int(cmd[2]))
            

def data_handler(packet):
    """
    Handler packets for data received.
    :param packet: Packet received.
    :type packet: dict
    """
    if packet["destination"] == ADDR:
        print(packet["payload"])
    else:
        send_packet(packet)


def update_handler(packet):
    """
    Handler packets for periodic update.
    :param packet: Packet received.
    :type packet: dict
    """
    payload = packet['payload']
    source = packet['source']
    if source not in table.routes:
        print("There is not " + source + " in table.")
        return
    distance_from_source = table.routes[source].min
    for key in payload:
        if key != ADDR:
            table.add_learned_router(key, distance_from_source + int(payload[key]), source)


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


def trace_handler(packet):
    """
    Handler packets for trace command.
    :param packet: Packet received.
    :type packet: dict
    """
    packet["hops"].append(ADDR)
    if packet["destination"] != ADDR:
        send_packet(packet)
    else:
        payload = json.dumps(packet)
        data_packet = create_data_packet(packet["source"], payload)
        send_packet(data_packet)


def recv_packet():
    """
    Thread for receive packets and handle.
    """
    while True:
        msg, ip = SOCK.recvfrom(1024)
        if len(msg) > 0:
            msg = bytes.decode(msg)
            packet = json.loads(msg)
            if packet["type"] == "update":
                update_handler(packet)
            elif packet["type"] == "data":
                data_handler(packet)
            elif packet["type"] == "trace":
                trace_handler(packet)
            # treat_function = get_treater(packet["type"])
            # treat_function(packet)


def create_trace_packet(destination):
    """
    Create a dictionary for trace to be send.
    :param destination: Router destination IP address.
    :type destination: str
    :return: Dictionary.
    :rtype: dict
    """
    return {
        "type": "trace",
        "source": ADDR,
        "destination": destination,
        "hops": [ADDR]
    }


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


def prompt():
    """
    Read commands and select the right function.
    """
    while True:
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
            destination = cmd[1]
            packet = create_trace_packet(destination)
            send_packet(packet)
        elif cmd[0] == "status":
            print(table.to_string())
        elif cmd[0] == "msg":
            if len(cmd) < 3:
                print("Too few arguments")
                continue
            destination = cmd[1]
            message = " ".join(cmd[2:])
            packet = create_data_packet(destination, message)
            send_packet(packet)
        elif cmd[0] == "help":
            print("add del trace data help quit")
        elif cmd[0] == "quit":
            sys.exit(0)
        else:
            print("Command not found")


def create_update_packet(destination, payload):
    return {
        "type": "update",
        "source": ADDR,
        "destination": destination,
        "payload": payload
    }


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
                if faster_route.destination != dest and faster_route.learned_from != dest and key != dest and faster_route.distance < MAX_LOOP_SIZE:
                    payload[key] = faster_route.distance

            # print('payload: ' + str(payload) + ' to : ' + dest)
            update_packet = create_update_packet(dest, payload)
            send_packet(update_packet)
                        
        # print(table.to_string())
        time.sleep(period)


def remove_outdated_routes(period):
    """
    Remove all options that have not been updated in 4 periods.
    :param period: Time in seconds.
    :type period: float
    """
    while True:
        time.sleep(period)
        # print("Tentando remover")
        now: float = time.time()

        table.routes = {addr: route for addr, route in table.routes.items() if len(route.options) > 0}

        for key in table.routes.keys():
            for indexOption, option in enumerate(table.routes[key].options):
                if (now - option.timestamp) >= (4 * period) and option.learned_from is not None:
                    # print("Excluindo")
                    del table.routes[key].options[indexOption]
                    table.routes[key].sort_options()
        table.routes = {addr: route for addr, route in table.routes.items() if len(route.options) > 0}


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("addr")
    parser.add_argument("period")

    parser.add_argument("--addr")
    parser.add_argument("--update-period")
    parser.add_argument("--startup-commands")

    args = parser.parse_args()
    
    global ADDR
    ADDR = args.addr
    print("Address: " + ADDR)

    period = int(args.period)
    print("Period: " + str(period))

    global SOCK
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SOCK.bind((ADDR, PORT))

    global table
    table = Table()

    if (args.startup_commands):
        startup = args.startup_commands
        startup_file = open(startup, "r")
        read_file(startup_file)

    t_recv = threading.Thread(target=recv_packet)
    t_recv.start()

    t_prompt = threading.Thread(target=prompt)
    t_prompt.start()

    t_update = threading.Thread(target=update, kwargs={'period': period})
    t_update.start()

    t_remove_outdated_routes = threading.Thread(target=remove_outdated_routes, kwargs={'period': period})
    t_remove_outdated_routes.start()

    t_prompt.join()
    

if __name__ == "__main__":
    main()
