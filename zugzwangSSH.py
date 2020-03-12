import socket
import paramiko

# Connecting credentials
CONST_USERNAME = "root"
CONST_PASSWD = "alpine"
CONST_PORT1 = 62078 # for all iphone connections
CONST_PORT2 = 22 # for connections on port 22 (jb)
local_addresses = []

def run():
    # get user IP address + range for scan
    sep = '.'
    user_IP = input("Enter <IP address>: ")
    user_IP = user_IP.split(sep)
    net_frame = user_IP[0] + sep + user_IP[1] + sep # beginning ip address frame
    ranges_for_scan = input("<minNetRange> <maxNetRange> <minHostRange> <maxHostRange>: ")
    ranges_for_scan = ranges_for_scan.split() # split to get the range #'s
    st1, en1, st2, en2 = [int(ranges_for_scan[i]) for i in (0,1,2,3)]
    
    print("Scanning ... this can take a few minutes\n")
    
    for ip1 in range(st1, en1+1):
        net_ID = net_frame + str(ip1) + sep
        for ip2 in range(st2,en2+1):
            addr = net_ID + str(ip2)
            if (scan(addr)):
                print(addr, "is live ... wrote to addresses")
                local_addresses.append(addr)
            else:
                print(addr)
                
    # verify that some addresses were found
    if len(local_addresses) == 0:
        print("\nNo devices were found.")
        exit()

    sshIntoDevice()

def scan(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(1)
    result = s.connect_ex((addr, CONST_PORT2)) 
    if result == 0:
        return 1
    else:
        return 0
    
def sshIntoDevice():
    for line in local_addresses:
        while True:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=line, username=CONST_USERNAME, password=CONST_PASSWD)

                print("\nCurrently connected to the following device(s): " + str(local_addresses) + "\n")
                
                while True:
                    command = input("Type in command to run (type 'stop' to end connection): ")
                    if command == "stop":
                        break
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
                    for line in iter(ssh_stdout.readline, ""):
                        print(line, end="")  # print the output of command
                ssh.close()
                break

            except paramiko.SSHException as SSHException:
                # if address isn't open
                print("Connection failed with device:", line)
                print("...")
                break

            except ConnectionError:
                # if other connection error
                print("Connection failed with device:", line)
                print("...")
                break

run()
