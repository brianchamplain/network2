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


class AsyncServer(asyncio.Protocol):
    server_info = {
        "USER_LIST": [],
        "MESSAGES": [],
    }

    error_list = {
        "user does not exist",
    }

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
        self.data = dict()
        print('Accepted connection from {}'.format(self.address))

    def add_user(self, username):
        if username not in AsyncServer.server_info["USER_LIST"]:
            self.transport.write(
                json.dumps(
                    {
                        "USERNAME_ACCEPTED": True,
                        "INFO": "welcome to the server, " + username + "!"
                    }.update(AsyncServer.server_info),
                    ensure_ascii=True
                ).encode('utf-8')
            )
            AsyncServer.server_info["USER_LIST"].append({username: self.transport})
        else:
            self.transport.write(
                json.dumps(
                    {
                        "USERNAME_ACCEPTED": False,
                        "INFO": "username " + username + " already exists."
                    },
                    ensure_ascii=True
                ).encode('utf-8')
            )

    def data_received(self, data):
        """
            receives and buffers data from the client based on a delimiter (b'?')

            pre:
                - data (bytes): data from the client

            post:
                - none
        """
        self.data = json.loads(data.decode('utf-8'))

        if self.data is not None:
            if "USERNAME" in self.data:
                self.add_user(self.data["USERNAME"])
            elif "MESSAGE" in self.data:
                message = self.data["MESSAGE"]
                if message[1] not in AsyncServer.server_info["USER_LIST"]:
                    self.transport.write(
                        json.dumps(
                            {
                                "ERROR": AsyncServer.error_list[0]
                            }, ensure_ascii=True
                        ).encode('utf-8')
                    )
                elif message[1] == 'ALL_USERS':
                    AsyncServer.server_info["MESSAGES"].append(message)
                    dump = json.dumps(
                        {
                            "MESSAGES": filter(
                                lambda x: x[1] == 'ALL',
                                AsyncServer.server_info["MESSAGES"],
                            )[0]
                        },
                        ensure_ascii=True
                    ).encode('utf-8')
                    message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
                    for i in AsyncServer.server_info["USER_LIST"]:
                        i.write(message_to_send)
                else:
                    AsyncServer.server_info["MESSAGES"].append(message)
                    dump = json.dumps(
                        {
                            "MESSAGES": filter(
                                lambda x: x[1] == message[1],
                                AsyncServer.server_info["MESSAGES"],
                            )[0]
                        },
                        ensure_ascii=True
                    ).encode('utf-8')
                    message_to_send = (struct.Struct('!I').pack(len(dump)) + dump)
                    AsyncServer.server_info["USER_LIST"][message[1]].write(message_to_send)
            else:
                print("err: no such val")
        else:
            print("err: no data received")

        json.dump(AsyncServer.server_info, 'SERVER_DATA.json')
        self.data = {}

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
        elif self.data:
            print('client {} sent {} but then closed'
                  .format(self.address, self.data))
        else:
            print('client at {} closed socket'.format(self.address))


if __name__ == '__main__':
    hostname = socket.gethostname()

    parser = argparse.ArgumentParser(description='chat client for newfangled chat service \"whatever you want\"')
    parser.add_argument('host', default=hostname, help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    #purpose = ssl.Purpose.CLIENT_AUTH
    #context = ssl.create_default_context(purpose, cafile='ca.crt')
    #context.load_cert_chain('localhost.pem')
    coro = loop.create_server(AsyncServer, args.host, args.p)
    server = loop.run_until_complete(coro)

    print('listening at {}:'.format(hostname + ' port ' + str(args.p)))
    try:
        loop.run_forever()
    finally:
        server.close()
        loop.close()
