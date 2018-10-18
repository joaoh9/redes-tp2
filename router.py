import sys
import threading
import json
import re
import socket

routes = {}
PORT = 55151
addr = None
package = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((sys.argv[1], PORT))
print("Address: " + sys.argv[1])


def add_link(receiver, distance):
    if receiver not in routes:
        routes[receiver] = [[receiver, distance]]
    else:
        for i in range(len(routes[receiver])):
            if receiver == routes[receiver][i][0]:
                print("Route " + receiver + " already added.")
                return
        routes[receiver].append[[receiver, distance]]
        sock.connect((receiver, PORT))
    print("Added route to " + receiver + " with distance " + str(distance))


def del_enlace(enlace):
    # ip = enlace[1]
    # ....
    print("Del enlace")


def prompt(addr):
    while 1:
        s = input("> ")
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
            print(output4)
        elif cmd[0] == "data":
            data = cmd[1]
            dest = cmd[2]
            send_data(data, sock, addr)
        elif cmd[0] == "quit":
            break
        else:
            print("Command not found")

def send_package(dest, package):
    msg = json.dumps(pacote)
    message = bytes(msg, 'utf-8')
    udp.sendto(message, (dest, PORT))

def recv_package(package):
    while True:
        msg, ip = sock.recvfrom(1024)
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


read_file(startup_file):
    print('read file')


def main():

    period = int(sys.argv[2])
    print("Period: " + str(period))
    
    # --startup-comands
    if len(sys.argv) > 3:
        startup = sys.argv[3]
        startup_file = open(startup, "r")
        read_file(startup_file)
    
    t_prompt = threading.Thread(target=prompt, kwargs={'addr': addr})
    t_prompt.start()

    t_listen = threading.Thread(target=recv_package, kwargs={'package': package})
    t_listen.start()

    t_prompt.join()
    

if __name__ == "__main__":
    main()
