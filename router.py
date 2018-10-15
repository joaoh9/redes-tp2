import sys
import threading

routes = []


def add_route(receiver, distance):
    index = -1
    for i in range(len(routes)):
        print("Checking " + receiver + " is " + str(routes[i][0]))
        if receiver == routes[i][0]:
            print("True")
            index = i
            break
    if index is -1:
        routes.append([receiver, [[receiver, distance]]])
    else:
        routes[index][1].append([receiver, distance])
        routes[index][1].sort(key=lambda x: x[1])
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
            add_route(cmd[1], int(cmd[2]))
        elif cmd[0] == "del":
            print("Run del")
        elif cmd[0] == "trace":
            print("Run trace")
        elif cmd[0] == "status":
            print(str(routes))
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

    t_prompt = threading.Thread(target=prompt, args=())
    t_prompt.start()
    t_prompt.join()


if __name__ == "__main__":
    main()