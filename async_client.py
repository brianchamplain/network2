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
import struct
import ast
import datetime
import calendar
import os


class AsyncClient(asyncio.Protocol):
    def __init__(self):
        self.username = ""
        self.logged_in = False
        self.header_struct = struct.Struct('!I')
        self.data = b''
        self.tuple = ()

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info("peername")
        print('accepted connection from {}'.format(self.address))
        os.system("cls")

    def send_message(self, data):
        length = self.header_struct.pack(len(data))
        self.transport.write(length + data)

    def data_received(self, data):
        """simply prints any data that is received"""
        # print(data)
        self.data += data
        if self.logged_in:
            self.print_messages(data)

    @asyncio.coroutine
    def handle_user_input(self, loop):
        """reads from stdin in separate thread
        if user inputs 'quit' stops the event loop
        otherwise just echos user input
        """
        while True:
            if not self.logged_in:
                message = yield from loop.run_in_executor(
                    None, input, 'enter a username (or type \"quit\" to quit)\n\n>>'
                )

                if message == "quit":
                    loop.stop()
                    return
                # store message for your self and send the username
                my_dict = {"USERNAME": message}
                string_message = json.dumps(my_dict).encode('utf-8')
                self.send_message(string_message)

                yield from asyncio.sleep(1.0)

                self.data = self.data[self.data.find(b"{"):]
                json_dict = json.loads(self.data.decode('utf-8'))

                if not json_dict["USERNAME_ACCEPTED"]:
                    print("\n", json_dict["INFO"], "\n")
                    self.data = b''
                elif json_dict["USERNAME_ACCEPTED"]:
                    print('\n' + json_dict['INFO'])

                    print('\nusers online:\n')
                    for i in json_dict["CURRENTLY_ONLINE"]:
                        if i != "SYSTEM":
                            print("\t- " + i)
                    print()

                    self.print_messages(self.data, init=True)
                    self.username = message
                    self.logged_in = True

            # If user is logged in
            else:
                message = yield from loop.run_in_executor(None, input)
                if message == "quit":
                    loop.stop()
                    return
                elif len(message) == 0:
                    print('you must enter a message')
                elif message[0] == "@":
                    # Send to an individual person
                    first_white_space = message.find(" ")
                    message = (
                        self.username, message[1:first_white_space],
                        datetime.datetime.now().strftime('%m.%d.%Y %I:%M%p'),
                        message[first_white_space + 1:]
                    )
                    send_message = json.dumps({'MESSAGE': message}).encode('utf-8')
                    self.send_message(send_message)
                else:
                    message = (self.username, "ALL", datetime.datetime.now().strftime('%m.%d.%Y %I:%M%p'), message)

                    dump = json.dumps({'MESSAGE': message}).encode('utf-8')
                    self.send_message(dump)

                yield from asyncio.sleep(1.0)

    def connection_lost(self, ex):
        print("Lost connection" + '\n')
        self.logged_in = False
        self.transport.close()

    def print_messages(self, data, init=False):
        if init:
            json_dict = json.loads(data.decode('utf-8'))
        else:
            json_dict = json.loads(data[data.find(b"{"):].decode('utf-8'))
            os.system('cls')

        if "ERROR" in json_dict:
            print("error: " + json_dict["ERROR"])
            print('--------------------------------------------')
            return

        for i in json_dict["MESSAGES"]:
            if i[1] == "ALL" or i[1] == self.username or i[0] == self.username:
                print(("{0:<16}@ {1}: {2}".format(str(i[0]), i[2], str(i[3]))))
        print('--------------------------------------------')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example client')
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default = 9000,
                        help='TCP port (default 9000)')
    parser.add_argument('-ca', dest='cafile', metavar='cafile', type=str, default=None,
                        help='CA File')
    # default for ca file can either be none or you can just leave it out it doesn't really matter
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    # we only need one client instance
    client = AsyncClient()

    purpose = ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose, cafile=args.cafile)

    coro = loop.create_connection(lambda: client, args.host, args.p, ssl=context, server_hostname='localhost')

    loop.run_until_complete(coro)

    # Start a task which reads from standard input
    asyncio.async(client.handle_user_input(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()