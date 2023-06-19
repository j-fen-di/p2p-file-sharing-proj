"""
Follow the instructions in each method and complete the tasks. We have given most of the house-keeping variables
that you might require, feel free to add more if needed. Hints are provided in some places about what data types 
can be used, others are left to user discretion, make sure that what you are returning from one method gets correctly
interpreted on the other end. 
At end of each timestep, after all clients have completed their actions, log the registered clients in the format below
{
    "time": <time>,
    "text": "Clients registered: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
"""
import socket
from textwrap import indent
import threading
import pickle
import json
import collections

class p2pbootstrapper:
    def __init__(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Initialize the socket object and bind it to the IP and port, refer  #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.     #
        ##############################################################################

        self.boots_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.boots_socket.bind((ip, port))
        self.clients = None  # None for now, will get updates as clients register
        #FORM OF CLIENTS- {client_id: (ip, port)}
        #print("socket bound")

        # Append the log to this variable.
        self.log = []

        # Timing variables:
        ###############################################################################################
        # TODO:  To track the time for all clients, self.time starts at 0, when all clients register  #
        #        self.MAX_CLIENTS is the number of clients we will be spinnign up. You can use this   #
        #        to keep track of how many 'complete' messages to get before incrementing time.       #
        #        CHange this when testing locally                                                     #
        ###############################################################################################
        self.time = 0
        self.MAX_CLIENTS = 20
        self.done = 0

    def start_listening(self):
        ##############################################################################
        # TODO:  This function will make the BS start listening on the port 8888     #
        #        Refer to                                                            #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.     #
        #        You will need to link each connecting client to a new thread (using #
        #        client_thread function below) to handle the requested action.       #
        ##############################################################################
        self.boots_socket.listen(self.MAX_CLIENTS)
        #print("bootstrapper listening")
        while True:
            clientSocket, addr = self.boots_socket.accept()
            #print("bs accepted client")
            thread = threading.Thread(target = self.client_thread, args=(clientSocket, addr))
            thread.start()
            #print("bs thread started")


    def client_thread(self, clientSocket, addr):
        ##############################################################################
        # TODO:  This function should handle the incoming connection requests from   #
        #        clients. You are free to add more arguments to this function based  #
        #        on your need                                                        #
        #        HINT: After reading the input from the buffer, you can decide what  #
        #        action needs to be done. For example, if the client wants to        #
        #        deregister, call self.deregister_client                             #
        ##############################################################################
        request = clientSocket.recv(1024).decode()
        #print("bs received: " + request)
        #request format is "requesttype(R or U or L or D);client_id;..."
        request = request.split(";")
        if request[0] == "R":
            ip = request[2]
            #print("client ip = " + str(ip))
            port = int(request[3])
            #print("client port = " + str(port))
            self.register_client(int(request[1]), ip, port)
            clientSocket.close()
        elif request[0] == "U":
            self.deregister_client(int(request[1]))
            clientSocket.close()
        elif request[0] == "L":
            pickled_clients = pickle.dumps(self.return_clients())
            clientSocket.send(pickled_clients)
            clientSocket.close()
        elif request[0] == "D":
            self.process_action_complete(request[1])
            clientSocket.close()   
        pass

    def register_client(self, client_id, ip, port):  
        ########################################################################################
        # TODO:  Add client to self.clients, if already present, update status to 'registered  #
        ########################################################################################
        #print("registered " + str(client_id))
        registered = "registered"
        if self.clients == None:
            self.clients = {client_id: (ip, port, registered)}
            #self.clients = {client_id: (ip, port)}
        else:
            self.clients[client_id] = (ip, port, registered)
        # elif client_id not in list(self.clients.keys()):
        #     self.clients[client_id] = (ip, port, registered)
        # #print("number of clients = " + str(len(self.clients)))
        # else:
        #     self.clients[client_id][2] = registered


    def deregister_client(self, client_id):
        ##############################################################################
        # TODO:  Update status of client to 'deregisterd'                            #
        ##############################################################################
        #print("deregistered " + str(client_id))
        deregistered = "deregistered"
        if self.clients == None:
            return
        elif client_id in list(self.clients.keys()):
            ip, port, status = self.clients[client_id]
            self.clients[client_id] = (ip, port, deregistered)
            #del self.clients[client_id]

    def return_clients(self):
        ##############################################################################
        # TODO:  Return self.clients                                                 #
        ##############################################################################
        return self.clients
        

    def start(self):
        ##############################################################################
        # TODO:  Start timer for all clients so clients can start performing their   #
        #        actions                                                             #
        ##############################################################################
        if self.time == 0:
            text = "Clients registered: "
            #orderedDict = collections.OrderedDict(sorted(self.clients.items()))
            for client in sorted (self.clients.keys()):
                if self.clients[client][2] == "registered":
                    entry = "<" + str(client) + ", " + str(self.clients[client][0]) + ", " + str(self.clients[client][1]) + ">, "
                    text = text + entry
            text = text[:-2]
            log_dict = {"time": self.time, "text": text}
            self.log.append(log_dict)

            newName = "bootstrapper"
            newFileName = "%s.json" % newName
            newFile = open(newFileName, "w")
            json_dict = json.dumps(self.log, indent=4)
            newFile.write(json_dict)
            newFile.close()
        self.time = self.time + 1
        print(self.time)
        startSignal = "S"
        for client in self.clients:
            # if self.clients[client][2] == "deregistered":
            #     continue
            print("START CLIENT No. " + str(client))
            ip, port = self.clients[client][0], self.clients[client][1]
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print("socket created")
            clientSocket.connect((ip, port))
            #print("socket connected")
            clientSocket.send(startSignal.encode())
            #print("start signal sent to " + str(client))
            clientSocket.close()
            #print("close")
        pass

    def process_action_complete(self, msg):
        ##############################################################################
        # TODO:  Process the 'action complete' message from a client,update time if  #
        #        all clients are done, inform all clients about time increment       #
        ##############################################################################
        #msg = client_id
        #print("done received")
        self.done += 1
        #print("num  done = " + str(self.done))
        if self.done == len(self.clients):
            self.done = 0
            #add to log
            text = "Clients registered: "
            #orderedDict = collections.OrderedDict(sorted(self.clients.items()))
            for client in sorted (self.clients.keys()):
                if self.clients[client][2] == "registered":
                    entry = "<" + str(client) + ", " + str(self.clients[client][0]) + ", " + str(self.clients[client][1]) + ">, "
                    text = text + entry
            text = text[:-2]
            log_dict = {"time": self.time, "text": text}
            self.log.append(log_dict)

            newName = "bootstrapper"
            newFileName = "%s.json" % newName
            newFile = open(newFileName, "w")
            json_dict = json.dumps(self.log, indent=4)
            newFile.write(json_dict)
            newFile.close()
            self.start()
        pass