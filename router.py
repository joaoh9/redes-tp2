import sys
import threading
import json
import re
import socket

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


def del_enlace(enlace):
    # ip = enlace[1]
    # ....
    print("Del enlace")


def prompt():
    while 1:
        s = input("> ")
        cmd = s.split()
        if len(cmd) is 0:
            continue
        elif cmd[0] == "add":
            add_link(cmd[1], int(cmd[2]))
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
        elif cmd[0] == "quit":
            break
        else:
            print("Command not found")


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
    sock.bind((addr, port))

    t_prompt = threading.Thread(target=prompt, args=())
    t_prompt.start()
    t_prompt.join()


if __name__ == "__main__":
    main()
