import sys

def main():
    addr = sys.argv[1]
    period = int(sys.argv[2])
    
    if sys.argv[3] is not None:
        startup = sys.argv[3]
        startup_file = open(startup, "r")

    while 1:
        cmd = input('')
        if cmd is 'quit':
            break

        enlace = cmd.split()
        if enlace[0] == 'ip'
            add_ip_to_interface(enlace)
        else if enlace[0] == 'add':
            add_enlace(enlace)
        else if enlace[0] == 'del':
            del_enlace(enlace)
        
def add_ip_to_interface(interface):
    # ip addr add <ip>/<prefixlen> dev <interface>
    address = interface[3].split('/')
    ip = address[0]
    prefixlen = address[1]

    interface = interface[6] #lo = loopback
    ....

def add_enlace(enlace):
    ip = enlace[1]
    weight = enlace[2]
    ....

def del_enlace(enlace):
    ip = enlace[1]
    ....
