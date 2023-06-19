from p2pbootstrapper import p2pbootstrapper
import time
import threading

# by Kayla Hunt and Justin Effendi

if __name__ == "__main__":
    ##############################################################################
    # You need to perform the following tasks:                                   #  
    # 1) Instantiate the bootstrapper                                            #
    # 2) Start listening on the well-known port                                  #
    # 3) Wait for 10 sec so that all clients come up and register                #
    # 4) Call bootst.start() which inturn calls the start of all clients         #
    ##############################################################################
    bootst = p2pbootstrapper()

    ##############################################################################
    #  We know that listening on a port is a blocking action, and the B.S        #
    #  cannot call start() once it starts listening. Threads to the rescue!     #
    #                                                                            #
    #  For step 2) create a thread to handle bootst.start_listening() method     #
    #  Now execute steps 3 and 4.                                                #
    ##############################################################################    

    # creating the thread and the lock
    bootst_thread = threading.Thread(target = bootst.start_listening)
    bootst_lock = threading.Lock()

    # running the function 'start_listening'
    #bootst_lock.acquire()
    bootst_thread.start()
    #bootst_lock.release()

    # 10 second delay for clients to come up/register
    #print("sleep")
    time.sleep(10)

    # call start of all clients
    #print("starting")
    bootst.start()