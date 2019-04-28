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

# module to create crypto random links and other
import secrets


# BLOCK GLOBAL VARIABLES
print_lock = threading.Lock()
client = MongoClient('mongodb://database:27017/')
db = client.buyqaw

# BLOCK CLASSES


class Admin:
    def __init__(self, data):
        # Admin panel:
        # register new users:
        # a/r;mailofadmin;amount;[{name: "Зеленый Квартал", id: "5544332211",
        # picture: "link", enter: [{name: "1A", picture: "link", MAC: "80:e6:50:02:a3:9a"}]}}]
        if data[2] == "r":
            self.output = "a/r;" + str(self.registeruser(data))
        # register new admins:
        # a/a;mailofadmin;amount;[{name: "Зеленый Квартал", id: "5544332211",
        # picture: "link", enter: [{name: "1A", picture: "link", MAC: "80:e6:50:02:a3:9a"}]}}]
        elif data[2] == "a":
            self.output = "a/a;" + str(self.registeruser(data))
        # TODO create other admin panel functions


    def registeruser(self, data):
        data = data.split(";")
        parent = data[1]
        amount = data[2]
        doors = json.loads(data[3])
        verifications = []
        for user in range(amount):
            user_id = str(secrets.token_hex(4)) + str(parent) + str(int(datetime.now().timestamp()))
            verification = secrets.token_urlsafe(32)
            verifications.append(verification)
            db.users.insert_one({"ID": user_id, "verification": verification, "doors": doors})
        return verifications


    def registeradmin(self, data):
        data = data.split(";")
        parent = data[1]
        amount = data[2]
        doors = json.loads(data[3])
        verifications = []
        for admin in range(amount):
            admin_id = str(secrets.token_hex(4)) + str(parent) + str(int(datetime.now().timestamp()))
            verification = secrets.token_urlsafe(32)
            verifications.append(verification)
            db.admins.insert_one({"ID": admin_id, "verification": verification, "doors": doors})
        return verifications


class Guest:
    def __init__(self, data):
        self.output = ""
        if data[0] == 'g' and data[2] == "?":
            data = data[3:].split(";")
            self.give_access(data)
        if data[0] == 'g' and data[2] == "!":
            data = data[3:].split(";")
            self.id = data[0]
            result = db.users.find_one({"ID": self.id})
            self.doors = result["doors"]
            self.name = result["name"]
            self.phone = result["phone"]
            self.verification = result["verification"]
            self.company = result["company"]
            self.position = result["position"]
            self.department = result['department']
            self.company = result['company']
            self.gverification = data[1]
            self.check_guest_link()

    def give_access(self, data):
        ID = data[0]
        doors = json.loads(data[1])
        ttl = data[2]
        result = db.users.find_one({"ID": ID})
        for building in result["doors"]:
            for door in range(len(doors)):
                if doors[door]["id"] == building["id"]:
                    doors[door]["idcheck"] = 1
                for eachdoor in range(len(doors[door])):
                    for eachcontroller in building["enter"]:
                        doors[door][eachdoor]["ttl"] = ttl
                        if doors[door][eachdoor]["MAC"] == eachcontroller["MAC"]:
                            doors[door][eachdoor]["controlleridcheck"] = 1
        try:
            for door in doors:
                if door["idcheck"] != 1:
                    raise ValueError('There is no accept')
                for cont in door["enter"]:
                    if cont["controlleridcheck"] != 1:
                        raise ValueError('There is no accept')
        except ValueError:
            item_doc = {
                'alarm': "Somebody trying to hack our guest algorithm",
                'timestamp': datetime.now()
            }
            db.alarms.insert_one(item_doc)

        id = int(datetime.now().timestamp() * 1000)
        verificationcode = secrets.token_urlsafe(32)
        item_doc = {
            'ID': id,
            'guestlink': verificationcode,
            'doors': doors
        }
        db.guests.insert_one(item_doc)

        self.output = verificationcode


    def check_guest_link(self):
        result = db.guests.find_one({"guestlink": self.gverification})
        if result:
            self.doors.extend(result["doors"])
            db.users.delete_many({"ID": self.id})
            item_doc = {
                'ID': self.id,
                'verification': self.verification,
                'name': self.name,
                'phone': self.phone,
                'position': self.position,
                'department': self.department,
                'company': self.company,
                'doors': self.doors
            }
            db.users.insert_one(item_doc)
            self.output = "r/" + str(self.id) + ";" + str(self.name) + ";" + str(self.position) + ";" \
                          + str(self.department) + ";" + str(self.company) + ";" + str(self.doors)
        else:
            self.output = "v/0"


# class to deal with registration process
class User:
    def __init__(self, data):

        self.id = ""
        self.doors = []

        if data[0] == "v":
            self.verificationcode = data[2:]
            self.check_first_reg()
            self.output = "v/" + str(self.id)
        elif data[0] == "r":
            data = data[2:].split(";")
            self.id = data[0]
            self.name = data[1]
            self.phone = data[2]
            self.position = data[3]
            self.department = data[4]
            self.company = data[5]
            self.register_new_user()

    def check_first_reg(self):
        result = db.users.find_one({"verification": self.verificationcode})
        if result:
            self.id = result["ID"]
        else:
            self.check_guest_link()

    def check_guest_link(self):
        result = db.guests.find_one({"guestlink": self.verificationcode})
        if result:
            self.doors = result["doors"]
            self.register_new_user_from_guest()
        else:
            self.id = "0"

    def register_new_user_from_guest(self):
        self.id = int(datetime.now().timestamp()*1000)
        item_doc = {
            'ID': self.id,
            'verification': self.verificationcode,
            'doors': self.doors
        }
        db.users.insert_one(item_doc)

    # This function
    def register_new_user(self):
        result = db.users.find_one({"ID": self.id})
        doors = result["doors"]
        db.users.delete_many({"ID": self.id})
        item_doc = {
            'ID': self.id,
            'verification': self.verificationcode,
            'name': self.name,
            'phone': self.phone,
            'position': self.position,
            'department': self.department,
            'company': self.company,
            'doors': doors
        }
        db.users.insert_one(item_doc)
        self.output = "r/" + str(self.id) + ";" + str(self.name) + ";" + str(self.position) + ";" \
                      + str(self.department) + ";" + str(self.company) + ";" + str(self.doors)


# TODO problem when initiating new door, add it to admin and users... Need to think about it
# TODO we can try to do it with Guest functionality...
# class to deal with new door
class Door:
    def __init__(self, data, days=365):
        # Request from admin`s page is: x/80:e6:50:02:a3:9a;A1;555444333;parent_zone_id;picture
        data = data.split(";")
        self.days = days
        self.id = data[0][2::]
        self.name = data[1]
        self.parent_id = data[2]
        self.picture = data[3]
        self.password = "060593"
        self.ttl = int(datetime.now().timestamp()) + self.days*86400
        self.output = ''
        self.parent_zone_id = ''
        self.register()

    def register(self):
        self.check()
        item_doc = {
            'name': self.name,
            'ID': self.id,
            'password': self.password,
            'ttl': self.ttl,
            'parent_id': self.parent_id,
            'parent_zone_id': self.parent_zone_id,
            'picture': self.picture
        }
        db.doors.insert_one(item_doc)
        self.output = "x/" + self.id + ";" + self.name + ";" + self.parent_id + ";"

    def check(self):
        result = db.doors.find_one({"ID": self.id})
        if result:
            db.doors.delete_many({"ID": self.id})
        else:
            pass


# class to give access
class Access:
    def __init__(self, data):
        request = data[3:].split(";")
        self.user_id = request[0]
        self.door_id = request[1]
        self.password = "0"
        self.ttl = "0"
        self.user = ''
        self.door = ''
        self.output = "a/"
        self.when = ''

        if data[2] == "?":
            self.check()
        else:
            self.logit(data)

    def check(self):
        self.door = db.doors.find_one({"ID": self.door_id})
        self.user = db.users.find_one({"ID": self.user_id})
        if self.door is None:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'alarm': "Enemy BuyNode with our algorithm",
                'timestamp': datetime.now()
            }
            db.alarms.insert_one(item_doc)
        elif self.user is None:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'alarm': "Hacker found",
                'timestamp': datetime.now()
            }
            db.alarms.insert_one(item_doc)
        else:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'alarm': "Request",
                'timestamp': datetime.now()
            }
            db.log.insert_one(item_doc)
            result = db.users.find_one({"doors.enter.MAC": self.door_id})
            if result:
                for buildings in result["doors"]:
                    for doors in buildings["enter"]:
                        try:
                            if doors["door_id"] == self.door_id:
                                self.password = doors["key"]
                                self.ttl = doors["ttl"]
                        except:
                            pass
        if self.password == "0":
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'timestamp': datetime.now(),
                'type': "Failure"
            }
            db.log.insert_one(item_doc)
        self.output += str(self.password) + ";" + str(self.ttl) + ";"

    def logit(self, request):  # a/!56303h43;80:e6:50:02:a3:9a;1555666261;
        request = request[3:].split(";")
        user_id = request[0]
        door_id = request[1]
        self.when = request[2]
        item_doc = {
            'user_id': self.user_id,
            'door_id': self.door_id,
            'timestamp': datetime.fromtimestamp(int(self.when)),
            'type': "Access"
        }
        db.log.insert_one(item_doc)
        return "a/!"


# class to handle request
class Request:
    def __init__(self, data, connection, addr):
        item_doc = {
            'data': data,
            'connection': addr,
            'timestamp': datetime.now(),
            'type': data[0]
        }
        db.lograw.insert_one(item_doc)
        self.data = data
        self.connection = connection
        self.output = ""
        if self.data[0] == "r" or self.data[0] == "v":
            info = User(data)
        elif self.data[0] == "x":
            info = Door(data)
        elif self.data[0] == "a":
            info = Access(data)
        elif self.data[0] == "g":
            info = Guest(data)
        else:
            info = "0"

        self.output = info.output
        self.connection.send(str(self.output).encode('utf-8'))


# class to handle TCP server
class TCPserver:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 7777

        self.sox = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sox.bind((self.host, self.port))
        print("socket binded to post", self.port)
        self.handle()
        self.sox.close()

    def handle(self):
        # put the socket into listening mode
        self.sox.listen(50)
        print("socket is listening")

        # a forever loop until client wants to exit
        while True:
            # establish connection with client
            connection, addr = self.sox.accept()

            # lock acquired by client
            print_lock.acquire()
            print('Connected to :', addr[0], ':', addr[1])

            # Start a new thread and return its identifier
            start_new_thread(self.server, (connection, addr,))

    # thread function
    def server(self, connection, addr):
        while True:
            # data received from client
            data = connection.recv(50000).decode('utf-8')
            if not data:
                print('Bye')
                # lock released on exit
                print_lock.release()
                break
            Request(data, connection, addr)
            # connection closed
        connection.close()

# BLOCK STATIC FUNCTIONS

# Populate with dummy values
def populate():
    Door("x/80:e6:50:02:a3:1a;1st floor;555444333;0;img/hello.png")
    Door("x/80:e6:50:02:a3:2a;2nd floor;555444333;0;img/hello.png")
    Door("x/80:e6:50:02:a3:3a;3rd floor;555444333;0;img/hello.png")
    Door("x/80:e6:50:02:a3:4a;4th floor;555444333;0;img/hello.png")
    Admin('a/r;Naboo;1;[{name: "Зеленый Квартал", id: "555444333", '
          'picture: "link", enter: '
          '[{name: "1st floor", picture: "img/hello.png", MAC: "80:e6:50:02:a3:9a"}]}}]')

# BLOCK MAIN
if __name__ == '__main__':
    # TCPserver()
    populate()



