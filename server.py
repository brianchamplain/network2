"""
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
import asyncio
import json
import argparse
import ssl
import struct
import datetime


class AsyncServer(asyncio.Protocol):
    server_info = {
        "USER_LIST": {"SYSTEM": '0'},
        "CURRENTLY_ONLINE": {"SYSTEM": '0'},
        "MESSAGES": [],
    }

    transports = {}

    error_list = [
        "user does not exist",
    ]

    def connection_made(self, transport):
        """
            prints connection data to the console

            pre:
                - transport: transport data from this instance of asyncio.Protocol

            post:
                - none
        """
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.data = b''
        print('Accepted connection from {}'.format(self.address))

    def add_user(self, username):
        """
            handles the creation of a user

            pre:
                - username (str): username to associate with given user
            post:
                - none
        """
        if username not in AsyncServer.server_info["USER_LIST"]\
                and username is not 'ALL'\
                and username is not 'SYSTEM'\
                and len(username) < 16:
            # append the username and the user's IP to the server info list
            AsyncServer.server_info["USER_LIST"].update({username: self.transport.get_extra_info('peername')})
            AsyncServer.server_info["CURRENTLY_ONLINE"].update({username: self.transport.get_extra_info('peername')})
            AsyncServer.transports.update({username: self.transport})

            # list of welcome info to send back to the user.
            # we have to do it like this, as we append the contents of AsyncServer.server_info to it.
            welcome_info = {
                "USERNAME_ACCEPTED": True,
                "INFO": "welcome to the server, " + username + "!"
            }

            # alert server that a new user has joined
            AsyncServer.server_info["MESSAGES"].append((
                'SYSTEM',
                'ALL',
                datetime.datetime.now().strftime('%m.%d.%Y %I:%M%p'),
                'user {} has connected'.format(username)
            ))

            # append server info and encode as JSON
            welcome_info.update(AsyncServer.server_info)
            dump = json.dumps(welcome_info, ensure_ascii=True).encode('utf-8')

            # frame and send the message
            message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
            self.transport.write(message_to_send)

            self.data = b''

        elif username is 'ALL' or username is 'SYSTEM':
            # we can do this in one command this time as we don't have to append data
            dump = json.dumps(
                {
                    "USERNAME_ACCEPTED": False,
                    "INFO": "username not allowed"
                }
            ).encode('utf-8')

            # frame and send the message
            message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
            self.transport.write(message_to_send)
        elif len(username) > 16:
            # we can do this in one command this time as we don't have to append data
            dump = json.dumps(
                {
                    "USERNAME_ACCEPTED": False,
                    "INFO": "username is too long. usernames must be less than 16 characters."
                }
            ).encode('utf-8')

            # frame and send the message
            message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
            self.transport.write(message_to_send)
        else:
            # we can do this in one command this time as we don't have to append data
            dump = json.dumps(
                {
                    "USERNAME_ACCEPTED": False,
                    "INFO": "username " + username + " already exists."
                }
            ).encode('utf-8')

            # frame and send the message
            message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
            self.transport.write(message_to_send)

    def data_received(self, data):
        """
            receives data and returns responses based on data

            pre:
                - data (bytes): data from the client

            post:
                - none
        """
        print(data.find(b'{'))
        self.data = json.loads(data[data.find(b'{'):].decode('utf-8'))
        print(self.data)

        if self.data is not None:
            if "USERNAME" in self.data:
                self.add_user(self.data["USERNAME"])
            elif "MESSAGE" in self.data:
                message = self.data["MESSAGE"]
                print(message[1])
                if message[1] not in AsyncServer.server_info["USER_LIST"]\
                   and message[1] != 'ALL':
                    self.transport.write(
                        json.dumps(
                            {
                                "ERROR": AsyncServer.error_list[0]
                            }, ensure_ascii=True
                        ).encode('utf-8')
                    )
                elif message[1] == 'ALL':
                    AsyncServer.broadcast(message)
                else:
                    AsyncServer.broadcast(message)
        else:
            print("err: no data received")

        # json.dump(AsyncServer.server_info, 'SERVER_DATA.json')
        self.data = b''

    def connection_lost(self, exc):
        """
            prints information about the disconnection of a client

            pre:
                - exc (str): exception information

            post:
                - none
        """
        if exc:
            print('client {} error: {}'.format(self.address, exc))
            AsyncServer.user_disconnected(self.address[0], "user {} has disconnected because of an error")
        elif self.data:
            print('client {} sent {} but then closed'.format(self.address, self.data))
            AsyncServer.user_disconnected(self.address[0], "user {} has disconnected")
        else:
            print('client at {} closed socket'.format(self.address))
            AsyncServer.user_disconnected(self.address[0], "user {} has disconnected")

    @staticmethod
    def broadcast(message):
        AsyncServer.server_info["MESSAGES"].append(message)

        messages_to_send = [x for x in AsyncServer.server_info["MESSAGES"] if x[1] == 'ALL']

        dump = json.dumps({"MESSAGES": messages_to_send}, ensure_ascii=True).encode('utf-8')
        message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)

        for i in AsyncServer.transports:
            AsyncServer.transports[i].write(message_to_send)

    @staticmethod
    def direct_message(message):
        AsyncServer.server_info["MESSAGES"].append(message)

        messages_to_send = [x for x in AsyncServer.server_info["MESSAGES"] if x[1] == message[1]]

        dump = json.dumps({"MESSAGES": messages_to_send}, ensure_ascii=True).encode('utf-8')

        message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
        AsyncServer.get_transport(message[1]).write(message_to_send)
        AsyncServer.get_transport(message[0]).write(message_to_send)

    @staticmethod
    def get_transport(username):
        users = AsyncServer.server_info["USER_LIST"]
        transports = AsyncServer.transports

        print(transports)
        for i in users:
            if i != "SYSTEM" and i == username and i in transports:
                return transports[i]


    @staticmethod
    def user_disconnected(ip, message):
        for i in AsyncServer.server_info["CURRENTLY_ONLINE"]:
            if ip == AsyncServer.server_info["CURRENTLY_ONLINE"][i][0]:
                AsyncServer.broadcast((
                    'SYSTEM',
                    'ALL',
                    datetime.datetime.now().strftime('%m.%d.%Y %I:%M%p'),
                    message.format(i)
                ))
                del AsyncServer.server_info["CURRENTLY_ONLINE"][i]
                return


if __name__ == '__main__':
    hostname = socket.gethostname()

    parser = argparse.ArgumentParser(description='chat client for newfangled chat service \"whatever you want\"')
    parser.add_argument('host', default=hostname, help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    purpose = ssl.Purpose.CLIENT_AUTH
    context = ssl.create_default_context(purpose, cafile='ca.crt')
    context.load_cert_chain('localhost.pem')
    coro = loop.create_server(AsyncServer, args.host, args.p, ssl=context)
    server = loop.run_until_complete(coro)

    print('listening at {}:'.format(hostname + ' port ' + str(args.p)))
    try:
        loop.run_forever()
    finally:
        server.close()
        loop.close()
