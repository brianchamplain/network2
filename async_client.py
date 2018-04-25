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
                self.username = message
                print(">Welcome! " + self.username + " Here's what you can do"
                      "\nEnter a message to send to all users"
                      "\n>Enter quit to quit"
                      "\n>Enter @username + message to send a direct message to a user"
                      "\n>Input: ")
                self.logged_in = True
                # need to implement to check if user is already in session
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
    purpose = ssl.Purpose.CLIENT_AUTH
    context = ssl.create_default_context(purpose, cafile=args.cafile)

    context.load_cert_chain(certfile)

    coro = loop.create_connection(lambda: client, args.host , 9000, context)

    loop.run_until_complete(coro)

    # Start a task which reads from standard input
    asyncio.async(client.handle_user_input(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()
