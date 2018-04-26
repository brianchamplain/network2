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

import socket
import time
import random
import asyncio

"""
counter = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", 9000))
sock.listen(100)

while True:
    conn, addr = sock.accept()
    print("Accepted connection from {}".format(addr))
    while True:
        conn.sendall(str(counter).encode("ascii"))
        time.sleep(3 * random.random())
        counter += 1
"""
#Example was given by josh are the above thingy here
#The below thingy is the one we work on
#code was adapted from the book chapter7 btw remember to put it in somewhere
class AsyncServer(asyncio.Protocol):
    def __init__(selfself, server, sock, name):
        self.users_list = []

    def connection_made(selfself,transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.data = b''
        print('accepted connection from {}'.format(self.address))

    def connection_lost(self, ex):
        #instead of using address gonna sub in username
        message = {self.username + "Has left"}
        #implement encode message
        self.broadcast(message)

    def message_handler(self, message):
        pass

    def broadcast(self,message):
        #broadcast to all users
        #haven't implement this thoroughly
        for user in self.users_list:
            #send message to each user #probably create a message handler before doing this
    def data_received(self, data):

if _name__ == '__main__':
    address = zen_utils.parse_command_line('asyncio server using callbacks')

    loop = asyncio.get_event_loop()

    coro = loop.create_server(AsyncServer, 9000)

    server = loop.run_until_complete(coro)
    purpose = ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose, cafile=cafile)
    for socket in server.sockets:
        print("Client: {}".formate(socket.getsockname()))

    try:
        loop.run_forever()
    finally:
        server.close
        loop.close()
