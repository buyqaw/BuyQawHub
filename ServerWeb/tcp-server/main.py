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
print_lock = threading.Lock()
client = MongoClient('mongodb://database:27017/')
db = client.buyqaw

# BLOCK CLASSES


# class to handle TCP server
class TCPserver:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 7777

        self.sox = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sox.bind((self.host, self.port))
        print("socket is bind to port", self.port)
        self.handle()
        self.sox.close()

    def handle(self):
        # put the socket into listening mode
        self.sox.listen(5000)
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
            try:
                # data received from client
                data = connection.recv(50000).decode('utf-8')
                print("Received data: ")
                print(data)
                if not data:
                    print('Bye')
                    # lock released on exit
                    print_lock.release()
                    break
                ser = self.Request(data, addr)
                connection.send(str(ser.output).encode('utf-8'))
            except Exception as ex:
                print("Error: " + str(ex))
                print_lock.release()
                break
        connection.close()

    # Subclass to handle request
    class Request:
        def __init__(self, request, addr):
            self.IP = addr[0]
            self.user = self.User()
            self.door = self.Door()
            self.access = self.Access()
            self.request = str(request)
            self.output = ""

            self.lograw()
            self.analyze()

        def analyze(self):
            # v/verification -> v/user_id
            # r/user_id;name;phone;position;department;company;email -> r/["name": name, "id": BID...

            # a/*user_id;MAC; -> a/1
            # a/?user_id;MAC; -> a/password;ttl;
            # a/!user_id;MAC;timestamp; -> a/1

            # e?MAC -> e/password -> e!

            # m?user_id -> m/icon;color;title;text; [or register function]

            # g/?user_id;[list of doors and buildings] -> g/!verification code

            # g/!user_id;verification_code
            print("Analyzing request in Request class")
            command = self.request[0]
            print()
            print("Command is: " + command)
            if command == "v":
                print("Action is verification, code is: ")
                print(self.request.split("/")[1].replace(";", ""))
                print()
                self.user.verification = self.request.split("/")[1].replace(";", "")
                self.user.verify()
                self.output = self.user.output
            elif command == "r":
                print()
                print("Action is registration, code is: ")
                print(self.request.split("/")[1])
                self.user.register(self.request)
                self.output = self.user.output
            elif command == "a":
                self.access.check(self.request)
                self.output = self.access.output


        def lograw(self):
            item_doc = {
                'data': self.request,
                'connection': self.IP,
                'timestamp': datetime.now(),
                'type': self.request[0]
            }
            db.lograw.insert_one(item_doc)

        # Subclass to handle user data and functions
        class User:
            def __init__(self):
                # Standard user data
                self.ID = None
                self.verification = None
                self.name = None
                self.email = None
                self.phone = None
                self.position = None
                self.department = None
                self.company = None
                self.creation = None
                self.created = None
                self.doors = None
                self.ttl = None
                self.workstart = None
                self.workend = None
                self.holidays = None

                self.registered = None

                # Admin user data
                self.isadmin = None
                self.admindoors = None
                self.adminbuildings = None
                self.admincreated = None
                self.admincreation = None

                # Output string
                self.output = None

            def verify(self):
                print("Started Request.verify method")
                print()
                if self.verifyolduser():
                    print("Did not find old user, start guest link verification")
                    print("Verification code is: ")
                    print(self.verification)
                    result = db.guest.find_one({"guestlink": str(self.verification)})
                    print()
                    print("Result of guest verification is: ")
                    pprint(result)
                    print()
                    if result:
                        self.registered = False
                        self.doors = result["doors"]
                        self.creation = datetime.now()
                        self.created = result["created"]
                        self.ttl = [result["ttl"]]*len(self.doors)
                        while True:
                            self.ID = secrets.token_urlsafe(16)
                            duplicate = db.user.find_one({"ID": self.ID})
                            if duplicate:
                                continue
                            else:
                                break
                        while True:
                            self.verification = str(secrets.token_urlsafe(16))
                            duplicate = db.user.find_one({"verification": self.verification})
                            if duplicate:
                                continue
                            else:
                                break
                        db.user.insert_one(self.__dict__)
                        print("Created new user: ")
                        pprint(self.__dict__)
                        print()
                    else:
                        print("Did not find guest link")
                        self.ID = "0"
                    self.output = "v/" + self.ID
                else:
                    self.generateoutput()

                print("Output value is: ")
                print(self.output)
                print("###################################")

            def verifyolduser(self):
                print("Started Request.verify old user method")
                print()
                result = db.guests.find_one({"verification": self.verification})
                print("Search result is: ")
                pprint(result)
                print()
                if result:
                    self.scan_user(result)
                    return False
                return True

            def register(self, request):
                # r/user_id;name;phone;position;department;company;email -> r/["name": name, "id": BID...
                request = request[2::].split(";")
                self.ID = request[0]
                print()
                print("User ID is: ")
                print(self.ID)
                print()
                print("Search for old user with this ID")
                olduser = db.user.find_one({"ID": self.ID})
                print("Old user is: ")
                pprint(olduser)
                if olduser:
                    self.registered = olduser["registered"]
                    print("Registered tag is: ")
                    print(self.registered)
                    print()
                    if self.registered:
                        print("Sending to update user data to admin")
                        self.update(olduser)
                    else:
                        print("Starting registration process")
                        wait = self.scan_user(olduser)
                        if wait:
                            self.phone = request[2]
                            self.email = request[6]
                            self.name = request[1]
                            self.position = request[3]
                            self.department = request[4]
                            self.company = request[5]
                            self.registered = True
                        print()
                        print("Our new user data is: ")
                        pprint(self.__dict__)
                        print()
                        if self.duplicates():
                            print("No duplicate was found")
                            self.generateoutput()

            def duplicates(self):
                # {"$or":[ {"vals":1700}, {"vals":100}]}
                user = db.user.find_one({"$or": [{"email": self.email}, {"phone": self.phone}]})
                if user:
                    # This user is already exists, please contact your administrator to receive verification code
                    print("Duplicate was found")
                    print()
                    self.output = "r/$"
                    return False
                return True

            def scan_user(self, user):
                print("Started to scan old data and merge with new data")
                # Standard user data
                self.ID = user["ID"]
                self.verification = user["verification"]
                self.email = user["email"]
                self.phone = user["phone"]
                self.position = user["position"]
                self.department = user["department"]
                self.company = user["company"]
                self.creation = user["creation"]
                self.created = user["created"]
                self.doors = user["doors"]
                self.ttl = user["ttl"]
                self.workstart = user["workstart"]
                self.workend = user["workend"]
                self.holidays = user["holidays"]

                # Admin user data
                self.isadmin = user["isadmin"]
                self.admindoors = user["admindoors"]
                self.adminbuildings = user["adminbuildings"]
                self.admincreated = user["admincreated"]
                self.admincreation = user["admincreation"]
                return 1

            def update(self, olduser):
                item_doc = {
                    'ID': self.ID,
                    'pending': True,
                    'updated': False,
                    "email": olduser["email"],
                    "phone": olduser["phone"],
                    "position": olduser["position"],
                    "department": olduser["department"],
                    "company": olduser["company"],
                    "newemail": self.email,
                    "newphone": self.phone,
                    "newposition": self.position,
                    "newdepartment": self.department,
                    "newcompany": self.company
                }
                db.lograw.insert_one(item_doc)
                self.output = "r/!"

            def generateoutput(self):
                print("Generating output")
                enters = self.generateoutputenters()
                print()
                print("Enters are: ")
                pprint(enters)
                head = str(self.ID) + ";" + str(self.name) + ";"
                head += str(self.phone) + ";" + str(self.position) + ";"
                head += str(self.department) + ";" + str(self.company) + ";"
                head += str(self.email) + ";"
                self.output = "r/" + head + enters + ";"
                print("Output is: ")
                print(self.output)
                print()

            def generateoutputenters(self):
                # r / ["name": name, "id": BID...
                fathers = []
                names = []
                pics = []
                doors = []
                print("Started loop to generate buildings string: ")
                for i in range(len(self.doors)):
                    door = self.doors[i]
                    result = db.door.find_one({"ID": door})
                    fathers.append(result["parent_ID"])
                    names.append(result["name"])
                    pics.append(result["picture"])
                    doors.append({"name": result["name"],
                                  "ttl": self.ttl[i], "key": result["password"],
                                  "picture": result["picture"], "MAC": result["ID"]})
                parents = list(set(fathers))
                enters = []
                for parent in parents:
                    enters.append({"id": parent, "enter": []})
                for i in range(len(fathers)):
                    father = fathers[i]
                    for j, dic in enumerate(enters):
                        if dic["id"] == father:
                            enters[j]["name"] = names[i]
                            enters[j]["picture"] = pics[i]
                            enters[j]["enter"].append(doors[i])
                return str(enters)


        class Door:
            def __init__(self):
                self.ID = None
                self.name = None
                self.parent_ID = None
                self.parent_zone_ID = None
                self.picture = None
                self.password = None
                self.created = None
                self.creation = None
                self.contractor = None

        class Access:
            def __init__(self):
                self.MAC = None
                self.user_id = None
                self.password = None
                self.ttl = None
                self.output = None

            # TODO finish it
            def check(self, request, addr):
                command = request[2]
                if command == "*":
                    item_doc = {
                        'ID': "DUCK!",
                        'user_id': self.user_id,
                        'door_id': self.door_id,
                        'timestamp': datetime.now(),
                        'type': "Failure"
                    }
                    db.log.insert_one(item_doc)

# BLOCK MAIN


if __name__ == '__main__':
    TCPserver()

