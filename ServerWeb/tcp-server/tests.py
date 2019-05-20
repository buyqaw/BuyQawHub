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
    buildings = {
        'BID': "1",
        "name": "testBuilding",
        "picture": ""
    }
    db.building.insert_one(buildings)
    boory = db.building.find_one({"BID": "1"})
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
    user = {
        'ID': "2",
        'registered': True,
        'verification': "warcbahrwcmi",
        'name': "test 2",
        'email': "test2",
        'phone': "test2",
        'position': "test2",
        'department': "test2",
        'company': "test2",
        'doors': [],
        'ttl': [],
        'creation': datetime.now(),
        'created': "1",
        'isadmin': False,
        'admindoors': [],
        'adminbuildings': [],
        'admincreated': "root",
        'admincreation': datetime.now(),
        "workstart": "9:00",
        "workend": "18:00",
        "holidays": [5, 6]
    }
    db.user.insert_one(user)
    usic = db.user.find_one({"ID": "2"})
    print("#### START OF TEST ####")
    print()
    print("Created door with this data: ")
    pprint(doory)
    print("")
    print("")
    print("Created building with this data: ")
    pprint(boory)
    print("")
    print("")
    print("Created guestlink with this data: ")
    pprint(gigi)
    print("")
    print("")
    print("Created test user with this data: ")
    pprint(usic)
    print("")
    print("")
    print("---------------------------")
    print("")
    print("")


class Test:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('tcp-server', 7777)
        self.guestLINK = None

    def verify_new_user(self):
        print()
        print("######################################")
        print("VERIFYING NEW USER")
        print()
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

    def create_new_guest(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('tcp-server', 7777)
        print()
        print("######################################")
        print("TESTING GUEST FUNCTIONALITY")
        print()
        self.sock.connect(self.server_address)
        print("Connected to TCP server")
        print()
        print("-----------------------------------")
        user = db.user.find_one({"ID": "1"})
        try:
            print("Sending guest access request from user 1")
            message = "g/?1;[{'name':'testBuilding','id':'1','picture':'','enter':" \
                      "[{'name':'test1','key':'060593','picture':'','MAC':'80:e6:50:02:a3:1a'}]}];"
            message += str(datetime.now().timestamp()) + ";"
            print()
            print('sending {!r}'.format(message))
            self.sock.sendall(message.encode('utf-8'))

            data = self.sock.recv(5000).decode("utf-8")
            print("Received value: ")
            print(data)
            self.guestLINK = data[2::]
            print()
            print("Generated guest link is: ")
            print(self.guestLINK)
            print()
        except:
            print("FAILS: no connection to the server...")

    def give_guest_access_to_old_user(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('tcp-server', 7777)
        print()
        print("######################################")
        print("GIVE ACCESS TO REGISTERED USER")
        print()
        self.sock.connect(self.server_address)
        print("Connected to TCP server")
        print()
        print("-----------------------------------")
        user = db.user.find_one({"ID": "2"})
        try:
            print("Sending guest access request from user 2")
            message = "g/!" + str(user["ID"]) + ";" + str(self.guestLINK) + ";"
            print()
            print('sending {!r}'.format(message))
            self.sock.sendall(message.encode('utf-8'))

            data = self.sock.recv(5000).decode("utf-8")
            print("Received value: ")
            print(data)
            print()
            print("Checking data base in the server side: ")
            pprint(db.user.find_one({"ID": "2"}))
            print()
            print()
        except:
            print("FAILS: no connection to the server...")


if __name__ == '__main__':
    populate()
    test = Test()
    test.verify_new_user()
    test.create_new_guest()
    test.give_guest_access_to_old_user()
