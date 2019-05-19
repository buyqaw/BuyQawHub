#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Bauyrzhan Ospan"
__copyright__ = "Copyright 2019, Buyqaw LLP"
__version__ = "1.0.1"
__maintainer__ = "Bauyrzhan Ospan"
__email__ = "bospan@cleverest.tech"
__status__ = "Development"

# BLOCK IMPORTS

# standard import of os
import os

# import random to create validation passwords
import random

from pprint import pprint

# import string to handle strings
import string

# import socket programming library
import socket

# import python-mongo library
from pymongo import MongoClient

# import thread module
from _thread import *
import threading

# import module to parse json
import json

# import datetime to deal with timestamps
from datetime import datetime
from datetime import timedelta

# module to create crypto random links and other
import secrets


# BLOCK GLOBAL VARIABLES
client = MongoClient('mongodb://database:27017/')
db = client.buyqaw


def populate():
    client.drop_database('buyqaw')
    doors = {
        'ID': "80:e6:50:02:a3:1a",
        "name": "test1",
        "parent_ID": 1,
        "parent_zone_ID": None,
        "picture": "",
        "ttl": 0,
        "password": "060593",
        "created": "root",
        "creation": datetime.now(),
        "contractor": "BuyQaw"
    }
    db.door.insert_one(doors)
    doory = db.door.find_one({"ID": "80:e6:50:02:a3:1a"})
    guest_links = {
        "ID": "1",
        "ttl": datetime.timestamp(datetime.now() + timedelta(days=100)),
        "guestlink": secrets.token_urlsafe(16),
        "doors": ["80:e6:50:02:a3:1a"],
        "created": "root",
        "creation": datetime.now()
    }
    db.guest.insert_one(guest_links)
    gigi = db.guest.find_one({"ID": "1"})


    print("#### START OF TEST ####")
    print()
    print("Created door with this data: ")
    pprint(doory)
    print("Created guestlink with this data: ")
    pprint(gigi)


class Test:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('tcp-server', 7777)

    def verify_new_user(self):
        self.sock.connect(self.server_address)
        print("Connected to TCP server")
        print()
        print("-----------------------------------")
        guest = db.guest.find_one({"ID": "1"})
        verification = guest["guestlink"]
        try:
            message = str('v/' + verification)
            print('sending {!r}'.format(message))
            self.sock.sendall(message.encode('utf-8'))

            data = self.sock.recv(5000).decode("utf-8")
            print('received {!r}'.format(data))
            user_id = str(data).split("/")[1]
            print("User ID is: " + user_id)

            print("-----------------------------------")
            print()
            print("Sending registration data")
            print()
            message = "r/" + user_id
            message += ";" + "Test User" + ";" + \
                       "+77777777777" + ";" + "CEO" + \
                       ";" + "Central" + ";" + "Bla Bla LLP" + \
                       ";" + "bla@bla.com" + ";"
            print('sending {!r}'.format(message))
            self.sock.sendall(message.encode('utf-8'))

            data = self.sock.recv(5000).decode("utf-8")
            print("Received value: ")
            print(data)
            print("####################################")
        finally:
            print('closing socket')
            self.sock.close()


if __name__ == '__main__':
    populate()
    test = Test()
    test.verify_new_user()
