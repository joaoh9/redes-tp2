import sys
import threading
import json
import re
import socket

routes = {}
PORT = 55151
addr = None

def add_link(receiver, distance, sock):
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


def prompt(sock, addr):
    while 1:
        s = input("> ")
        cmd = s.split()
        if len(cmd) is 0:
            continue
        elif cmd[0] == "add":
            add_link(cmd[1], int(cmd[2]), sock)
        elif cmd[0] == "del":
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

#def send_data(data, sock, dest):
#    json.dumps({"type": "data", "source": addr, "destination": dest , "payload": data})


def listen(sock):
    sock.listen()
    udpsock, addr = sock.accept()
    print ('Connected to router ' + str(addr))
    #while 1:
    data = udpsock.recv(1024)

def main():
    addr = sys.argv[1]
    print("Address: " + addr)
    period = int(sys.argv[2])
    print("Period: " + str(period))
    if len(sys.argv) > 3:
        startup = sys.argv[3]
        startup_file = open(startup, "r")
        print("Startup file name: " + startup)


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((addr, PORT))
    
    t_prompt = threading.Thread(target=prompt, kwargs={'sock': sock, 'addr': addr})
    t_prompt.start()

    t_listen = threading.Thread(target=listen, kwargs={'sock': sock})
    t_listen.start()

    t_prompt.join()
    

if __name__ == "__main__":
    main()
