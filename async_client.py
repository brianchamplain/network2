"""async_client

Champlain College CSI-235, Spring 2018
Prof. Josh Auerbach

Bare bones example of asynchronously receiving 
data from server and user input from stdin


    Author: Brian Nguyen and Jake Buzzell
    Class   : CSI-235
    Assignment: Final Project
    Date Assigned: April 11,2018
    Due Date: April 26, 2018  11:59pm
    Description:
        This code has been adapted from that provided by Prof. Joshua Auerbach:
        Champlain College CSI-235, Spring 2018
        The following code was provided by Prof. Joshua Auerbach
        and modified by Brian Nguyen and Jake Buzzell
"""
import asyncio
import argparse
import socket
import time
import ssl
import json


class AsyncClient(asyncio.Protocol):
    def __init__(self):
        self.username = ""
        self.logged_in = False



    def connection_made(self,transport):
        self.transport = transport
        self.address = transport.get_extra_info("peername")
        print('accepted connection from {}'.format(self.address))

    def data_received(self, data):
        """simply prints any data that is received"""
        print("received: ", data)
        json_dict = json.loads(data)

        if "USERNAME_ACCEPTED" in json_dict:
            boolean = json_dict.get("USERNAME_ACCEPTED")
            if boolean == True:
                self.logged_in = True
                print(">Welcome! " + self.username + " Here's what you can do"
                  "\nEnter a message to send to all users"
                  "\n>Enter quit to quit"
                  "\n>Enter @username + message to send a direct message to a user"
                  "\n>Input: ")

                if "INFO" in json_dict:
                    print("Info: " + json_dict.get("INFO") + '\n')
                elif "USER_LIST: " in json_dict:
                    print("User list: " + json_dict.get("USER_LIST") + '\n')
                elif "MESSAGES" in json_dict:
                    print("Messages: " + json_dict.get("MESSAGES") + '\n')

                elif "USERS_JOINED" in json_dict:
                    print("New user(s) joined: " + json_dict.get("USERS_JOINED") + '\n')
                elif "USERS_LEFT" in json_dict:
                    print("User(s) left: " + json_dict.get("USERS_LEFT") + '\n')

            elif boolean == False:
                print(json_dict.get("INFO") + '\n')
        else:
            print("Unexpected error: " + json_dict.get("INFO") + '\n')

    def send_message(self, data):
        message = bytes(data, 'utf-8')
        self.transport.write(message)

    def connection_lost(self, ex):
        print("Lost connection" + '\n')
        self.logged_in = False
        self.transport.close()



    @asyncio.coroutine
    def handle_user_input(self, loop):
        """reads from stdin in separate thread

        if user inputs 'quit' stops the event loop
        otherwise just echos user input
        """
        while True:
            if(self.logged_in == False):
                message = yield from loop.run_in_executor(None, input, ">Enter Username to log in \n"
                                                                       ">or Enter quit to quit \n"
                                                                       ">input: ")
                if message == "quit":
                    loop.stop()
                    return
                #store message for your self and send the username
                self.username = message
                my_dict = {"USERNAME": message}
                coded_message = json.dumps(my_dict)
                self.send_message(coded_message)

                yield from asyncio.sleep(1.0)
               

            #If user is logged in
            else:
                message = yield from loop.run_in_executor(None, input, ">")
                if message == "quit":
                    loop.stop()
                    return
                if message[0] == "@":
                    # haven't figured out how to store messages really
                    #Haven't implemented send direct message function yet
                    self.send_direct_message(message)
                #haven't implemented send message function yet
                self.send_message(message)
                yield from asyncio.sleep(1.0)
               

    def connection_lost(self, ex):
        self.transport.close()
        self.logged_in = False
        return




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example client')
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default = 9000,
                        help='TCP port (default 9000)')
    parser.add_argument('-ca', dest='cafile', metavar='cafile', type=str, default=None,
                        help='CA File')
    #default for ca file can either be none or you can just leave it out it doesn't really matter
    args = parser.parse_args()



    loop = asyncio.get_event_loop()
    # we only need one client instance
    client = AsyncClient()

    # the lambda client serves as a factory that just returns
    # the client instance we just created
    #purpose = ssl.Purpose.CLIENT_AUTH
	#context = ssl.create_default_context(purpose, cafile=args.cafile)
    #context.load_cert_chain(certfile)

    coro = loop.create_connection(lambda: client, args.host , args.p)

    loop.run_until_complete(coro)

    # Start a task which reads from standard input
    asyncio.async(client.handle_user_input(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()
