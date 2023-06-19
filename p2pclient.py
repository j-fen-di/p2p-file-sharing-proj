"""
Follow the instructions in each method and complete the tasks. We have given most of the house-keeping variables
that you might require, feel free to add more if needed. Hints are provided in some places about what data types 
can be used, others are left to students' discretion, make sure that what you are returning from one method gets correctly
interpreted on the other end. Most functions ask you to create a log, this is important
as this is what the auto-grader will be looking for.
Follow the logging instructions carefully.
"""

"""
Appending to log: every time you have to add a log entry, create a new dictionary and append it to self.log. The dictionary formats for diff. cases are given below
Registraion: (R)
{
    "time": <time>,
    "text": "Client ID <client_id> registered"
}
Unregister: (U)
{
    "time": <time>,
    "text": "Unregistered"
}
Fetch content: (Q)
{
    "time": <time>,
    "text": "Obtained <content_id> from <IP>#<Port>
}
Purge: (P)
{
    "time": <time>,
    "text": "Removed <content_id>"
}
Obtain list of clients known to a client: (O)
{
    "time": <time>,
    "text": "Client <client_id>: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
Obtain list of content with a client: (M)
{
    "time": <time>,
    "text": "Client <client_id>: <content_id>, <content_id>, ..., <content_id>"
}
Obtain list of clients from Bootstrapper: (L)
{
    "time": <time>,
    "text": "Bootstrapper: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
"""
import socket
import time
import json
import random
import threading
import pickle

class p2pclient:
    def __init__(self, client_id, content, actions):
        
        ##############################################################################
        # TODO: Initialize the class variables with the arguments coming             #
        #       into the constructor                                                 #
        ##############################################################################

        self.client_id = client_id
        self.content = content
        self.actions = actions  # this list of actions that the client needs to execute
        self.allClients = [] #this is a list of all clients known to bootstrapper used for query and search

        self.content_originator_list = None  # None for now, it will be built eventually

        ##################################################################################
        # TODO:  You know that in a P2P architecture, each client acts as a client       #
        #        and the server. Now we need to setup the server socket of this client   #
        #        Initialize the the self.socket object on a random port, bind to the port#
        #        Refer to                                                                #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.         #
        ##################################################################################

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        random.seed(int(self.client_id))
        self.randomPort = random.randint(9000, 9999)
        self.ip = '127.0.0.1'
        self.socket.bind(('127.0.0.1', self.randomPort))
        #print("Socket bound")
        #socket for connecting to the bootstrapper
        

        ##############################################################################
        # TODO:  Register with the bootstrapper by calling the 'register' function   #
        #        Make sure you communicate to the B.S the serverport that this client#
        #        is running on to the bootstrapper.                                  #
        ##############################################################################
        #self.register()
        
        ##############################################################################
        # TODO:  You can set status variable based on the status of the client:      #
        #        Registered: if registered to bootstrapper                           #
        #        Unregistered: unregistred from bootstrapper                         #
        #        Feel free to add more states if you need to                         #
        #        HINT: You may find enum datatype useful                             #
        ##############################################################################
        #possible statuses are: registered, unregistered, started
        self.status = "unregistered"

        # 'log' variable is used to record the series of events that happen on the client
        # Empty list for now, update as we take actions
        # See instructions above on how to append to log
        self.log = []

        # Timing variables:
        ###############################################################################################
        # TODO:  Ensure that you're doing actions according to time. B.S dictates time. Update this   #
        #        variable when BS sends a time increment signal                                       #
        ###############################################################################################
        self.time = 0
        self.register()

    def start_listening(self):
        ##############################################################################
        # TODO:  This function will make the client start listening on the randomly  #
        #        chosen server port. Refer to                                        #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.     #
        #        You will need to link each connecting client to a new thread (using #
        #        client_thread function below) to handle the requested action.       #
        ##############################################################################
        self.socket.listen()
        #print("socket listening")
        while True:
            otherClientSocket, addr = self.socket.accept()
            #print("Client accepted")
            thread = threading.Thread(target = self.client_thread, args=(otherClientSocket, addr))
            thread.start()
            #print("Client thread started")

    def client_thread(self, clientSocket, addr):
        ##############################################################################
        # TODO:  This function should handle the incoming connection requests from   #
        #        other clients.You are free to add more arguments to this function   #
        #        based your need                                                     #
        #        HINT: After reading the input from the buffer, you can decide what  #
        #        action needs to be done. For example, if the client is requesting   #
        #        list of known clients, you can return the output of self.return_list_of_known_clients #
        ##############################################################################
        request = clientSocket.recv(1024).decode()
        #print("received")
        #Decide action here
        if request == "R":
            self.register()
            clientSocket.close()
        elif request == "U":
            self.deregister()
            clientSocket.close()
        elif request == "L":
            self.query_bootstrapper_all_clients()
            clientSocket.close()
        elif request == "M":
            pickle_content_list = pickle.dumps(self.return_content_list())
            clientSocket.send(pickle_content_list)
            clientSocket.close()
        elif request == "O":
            pickle_known_clients = pickle.dumps(self.return_list_of_known_clients())
            clientSocket.send(pickle_known_clients)
            clientSocket.close()
        elif request == "S":
            self.start()
            clientSocket.close()      
        pass

    def register(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Register with the bootstrapper. Make sure you communicate the server#
        #        port that this client is running on to the bootstrapper.            #
        #        Append an entry to self.log that registration is successful         #
        ##############################################################################
        #print("registering")
        message = "R;" + str(self.client_id) + ";" + str(self.ip) + ";" + str(self.randomPort)
        BsTempClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BsTempClientSocket.connect((ip,port))
        BsTempClientSocket.send(message.encode())
        BsTempClientSocket.close()
        #self.socket.connect((ip, port))
        #self.socket.send(message.encode())
        text = "Client ID " + str(self.client_id) + " registered"
        logDict = {"time": self.time, "text": text}
        self.log.append(logDict)
        self.status = "registered"
        pass


    def deregister(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Deregister/re-register with the bootstrapper                        #
        #        Append an entry to self.log that deregistration is successful       #
        ##############################################################################
        #print("deregistering")
        message = "U;" + str(self.client_id)
        #self.socket.connect((ip, port))
        BsTempClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BsTempClientSocket.connect((ip,port))
        BsTempClientSocket.send(message.encode())
        BsTempClientSocket.close()
        text = "Unregistered"
        logDict = {"time": self.time, "text": text}
        self.log.append(logDict)
        self.status = "unregistered"
        pass

    def start(self):
        ##############################################################################
        # TODO:  When the Bootstrapper sends a start signal, the client starts       #
        #        executing its actions. Once this is called, you have to             #
        #        start reading the items in self.actions and start performing them   #
        #        sequentially, at the time they have been scheduled for, and as timed#
        #        by B.S. Once you complete an action, let the B.S know and wait for  #
        #        B.S's signal before continuing to next action                       #
        ##############################################################################

        ##############################################################################
        # TODO:  ***IMPORTANT***                                                     #
        # At the end of your actions, “export” self.log to a file: client_x.json,    #
        # this is what the autograder is looking for. Python’s json package should   #
        # come handy.                                                                #
        ##############################################################################
        self.time += 1
        #print("current timestep: " + str(self.time))
        done = "D;"
        BsTempClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BsTempClientSocket.connect(('127.0.0.1', 8888))
        # complete actions in x.json sequentially
        if (self.actions == []):
            BsTempClientSocket.send(done.encode())
        else:
            for action in self.actions:
                if (self.time == action["time"]):
                    #print(action["code"])
                    if action["code"] == "Q":
                        self.request_content(action["content_id"])
                    elif action["code"] == "R":
                        self.register()
                    elif action["code"] == "U":
                        self.deregister()
                    elif action["code"] == "L":
                        self.query_bootstrapper_all_clients()
                    elif action["code"] == "M":
                        self.query_client_for_content_list(int(action["client_id"]))
                    elif action["code"] == "O":
                        self.query_client_for_known_client(int(action["client_id"]))
                    elif action["code"] == "P":
                        self.purge_content(action["content_id"])
            BsTempClientSocket.send(done.encode())
        BsTempClientSocket.close()
        # create new file name and export self.log to client_x.json
        newName = "client_" + str(self.client_id)
        newFileName = "%s.json" % newName
        newFile = open(newFileName, "w")
        json_dict = json.dumps(self.log, indent=4)
        newFile.write(json_dict)
        newFile.close()
        pass

    #TODO: clarify on logging
    def query_bootstrapper_all_clients(self):
        ##############################################################################
        # TODO:  Use the connection to ask the bootstrapper for the list of clients  #
        #        registered clients.                                                 #
        #        Append an entry to self.log                                         #
        ##############################################################################
        request = "L;"
        #should be registered, so send into open socket
        BsTempClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BsTempClientSocket.connect(("127.0.0.1",8888))
        BsTempClientSocket.send(request.encode())
        bsClientList = BsTempClientSocket.recv(1024)
        BsTempClientSocket.close()
        bsClientList = pickle.loads(bsClientList)
        #bsClientList is list of dicts client_id:(ip, port, status)
        text = "Bootstrapper: "
        for id in bsClientList:
            entry = "<" + str(id) + ", " + str(bsClientList[id][0]) + ", " + str(bsClientList[id][1]) + ">, "
            text = text + entry
        text = text[:-2]
        logDict = {"time": self.time, "text": text}
        self.log.append(logDict)
        self.allClients = bsClientList
        pass

    #TODO: clarify on logging
    def query_client_for_known_client(self, client_id):
        client_list = None
        ##############################################################################
        # TODO:  Connect to the client and get the list of clients it knows          #
        #        Append an entry to self.log                                         #
        ##############################################################################
        self.query_bootstrapper_all_clients()
        if self.log != []:
            del self.log[-1]
        #self.allclients is list of dicts client_id:(ip, port, status)
        ip, port = self.allClients[client_id][0], self.allClients[client_id][1]
        clientTempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientTempSock.connect((ip, port))
        message = "O"
        clientTempSock.send(message.encode())
        #response will be list of all clients that the client knows
        content_orig_list = clientTempSock.recv(1024)
        content_orig_list = pickle.loads(content_orig_list)
        clientTempSock.close()
        text = "Client " + str(client_id) + ": "
        if content_orig_list != None:
            for content in content_orig_list:
                tup = content_orig_list[content]
                entry = "<" + str(tup[0]) + ", " + str(tup[1]) + ", " + str(tup[2]) + ">, "
                text = text + entry
            text = text[:-2]
            log_dict = {"time" : self.time, "text" : text}
            self.log.append(log_dict)
        else:
            log_dict = {"time": self.time, "text": "Client " + str(client_id) + ": "}
            self.log.append(log_dict)
        return client_list


    def return_list_of_known_clients(self):
        ##############################################################################
        # TODO:  Return the list of clients known to you                             #
        #        HINT: You can make a set of <client_id, IP, Port> from self.content_originator_list #
        #        and return it.                                                      #
        ##############################################################################
        # client_list = []
        # #content_originator_list = {content_id: (client_id, IP, Port)}
        # for content_id in self.content_originator_list:
        #     (clientId, IP, Port) = self.content_originator_list[content_id]
        #     client_list.append((clientId, IP, Port))
        # return client_list
        return self.content_originator_list

    def query_client_for_content_list(self, client_id):
        content_list = None
        ##############################################################################
        # TODO:  Connect to the client and get the list of content it has            #
        #        Append an entry to self.log                                         #
        ##############################################################################
        self.query_bootstrapper_all_clients()
        if self.log != []:
            del self.log[-1]
        #self.allclients is list of dicts client_id:(ip, port, status)
        #print(client_id)
        #print(self.allClients)
        ip, port = self.allClients[client_id][0], self.allClients[client_id][1]
        clientTempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientTempSock.connect((ip, port))
        message = "M"
        clientTempSock.send(message.encode())
        #response will be list of all content that the client had
        content_list = clientTempSock.recv(1024)
        content_list = pickle.loads(content_list)
        clientTempSock.close()
        if content_list != None:
            text = "Client " + str(client_id) + ": "
            for content_id in content_list:
                entry =  str(content_id) + ", "
                text = text + entry
            text = text[:-2]
            log_dict = {"time": self.time, "text": text}
            self.log.append(log_dict)
        return content_list

    def return_content_list(self):
        ##############################################################################
        # TODO:  Return the content list that you have (self.content)                #
        ##############################################################################
        return self.content
        pass

    def request_content(self, content_id):
        #####################################################################################################
        # TODO:  Your task is to obtain the content and append it to the                                    #
        #        self.content list.  To do this:                                                            #
        #        Get the content as per the instructions in the pdf. You can use the above query_*          #
        #        methods to help you in fetching the content.                                               #
        #        Make sure that when you are querying different clients for the content you want, you record#
        #        their responses(hints, if present) appropriately in the self.content_originator_list       #
        #        Append an entry to self.log that content is obtained                                       #
        #####################################################################################################
        
        search = True
        if content_id in self.content:
            #print("in content list")
            search = False
            return
        #self.content_originator_list is a dictionary content_id:(client_id, ip, port)
        elif self.content_originator_list != None and content_id in self.content_originator_list:
            #get list of content the client had
            (client_id, ip, port) = self.content_originator_list[content_id]
            #print("in COL, query client for content list")
            content_list = self.query_client_for_content_list(int(client_id))
            #remove entry from log bc not in client's action list
            if self.log != []:
                del self.log[-1]
            #if peer had the content, already in COL
            if content_id in content_list:
                #print("peer from content orig list had content")
                search = False
                self.content.append(content_id)
                #APPEND TO LOG
                text = "Obtained " + str(content_id) + " from " + str(ip) + "#" + str(port)
                log_dict = {"time": self.time, "text":text}
                self.log.append(log_dict)
                return

        #DO EXTENSIVE SEARCH FOR CONTENT, not in COL OR COL is NONE
        #get all clients list from p2ptracker, function sets the self.allClients variable
        #print("query bootstrapper for all clients")
        self.query_bootstrapper_all_clients()
        if self.log != []:
            del self.log[-1]
        BSClientList = self.allClients
        #print(BSClientList)
        while search:
            #dictionary of client_id:(ip, port, registered)
            #send request to each client serially
            for clientid in BSClientList:
                if int(clientid) == self.client_id:
                    continue
                (ip, port, status) = BSClientList[clientid]
                #(ip, port) = BSClientList[clientid]
                
                
                content_from_client = self.query_client_for_content_list(clientid)
                if self.log != []:
                    del self.log[-1]
                #print("queried for content list of client id " + str(clientid))
                #print("content from peer is " + str(content_from_client))
                if content_from_client != None and content_id in content_from_client: #response is list of content_id's (content list)
                    #data in peer's content list, receive content, add to content list, append to log
                    #print("data in peer's content list")
                    self.content.append(content_id)
                    #content_originator_list = {content_id: (client_id, IP, Port)}
                    if self.content_originator_list == None:
                        self.content_originator_list = {content_id:(clientid, ip, port)}
                    else:
                        self.content_originator_list[content_id] = (clientid, ip, port)
                    #APPEND TO LOG
                    text = "Obtained " + str(content_id) + " from " + str(ip) + "#" + str(port)
                    log_dict = {"time": self.time, "text":text}
                    self.log.append(log_dict)
                    search = False
                    return
                
                else: #if not sent content, then use hints (query the clients content originator list)
                    #print("using hints")
                    col_from_client = self.query_client_for_known_client(clientid)
                    if self.log != []:
                        del self.log[-1]
                    i = 0
                    while i < 2:
                        #col_from_client = self.query_client_for_known_client(clientid)
                        #format of col_from_client is list of {contentID: (clientid, ip, port)} dictionary
                        if col_from_client != None and content_id in col_from_client.keys():
                            #hint is helpful
                            hintedClient = col_from_client[content_id] #(clientid, ip, port)
                            hintedContent = self.query_client_for_content_list(hintedClient[0])
                            if self.log != []:
                                del self.log[-1]
                            hintedCOL = self.query_client_for_known_client(hintedClient[0])
                            if self.log != []:
                                 self.log[-1]
                            if content_id in hintedContent:
                                #hinted client has content, search stops
                                self.content.append(content_id)
                                self.content_originator_list[content_id] = hintedClient
                                text = "Obtained " + str(hintedClient[0]) + " from " + str(hintedClient[1]) + "#" + str(hintedClient[2])
                                log_dict = {"time": self.time, "text":text}
                                self.log.append(log_dict)
                                search = False
                                return
                            #hinted client doesnt have content, see if mention of content in COL
                            elif content_id in list(hintedCOL.keys()):
                                col_from_client = hintedCOL
                                i += 1
                                continue
                            #else:
                            #hinted client doesn't have mention of content in COL, hint not useful, return to original list    
                        #ELSE
                        #hint not useful, client goes back to original list
                        i += 1

            #if search is still true, then create a bigger list of clients
            #request every p2p client from tracker list for list of all other clients that client knows about
            #client_id:(ip, port, status)
            #print("use extended list")
            p2pList = {}
            registered = "registered"
            for clientID in BSClientList:
                if int(clientID) == self.client_id:
                    continue
                if clientID not in list(p2pList.keys()):
                    p2pList[clientID] = (BSClientList[clientID][0], BSClientList[clientID][1], registered)
                    #p2pList[clientID] == (BSClientList[clientID][0], BSClientList[clientID][1])
                else:
                    COL = self.query_client_for_known_client(clientID)
                    if self.log != []:
                        del self.log[-1]
                    for contentID in COL:
                        #COL = {contentid: (clientid, ip, port)}
                        if COL[contentID][0] not in list(p2pList.keys()):
                            p2pList[COL[contentID][0]] = (COL[contentID][1], COL[contentID][2], registered)
                            #p2pList[COL[contentID][0]] == (COL[contentID][1], COL[contentID][2])
            BSClientList = p2pList
            continue
        
        pass

    def purge_content(self, content_id):
        #####################################################################################################
        # TODO:  Delete the content from your content list                                                  #
        #        Append an entry to self.log that content is purged                                         #
        #####################################################################################################
        #print("Self.content is " + str(self.content))
        #print("content id to purge is " + str(content_id))
        if self.content != None and content_id in self.content:
            self.content.remove(content_id)
            text = "Removed " + str(content_id)
            purge = {"time": self.time, "text": text}
            self.log.append(purge)
        pass
        
