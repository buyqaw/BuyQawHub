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
from ast import literal_eval

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
            self.user = User()
            self.door = Door()
            self.access = Access()
            self.message = Message()
            self.guest = Guest()
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
                self.access.check(self.request, self.IP)
                self.output = self.access.output
            elif command == "g":
                self.guest.giveaccess(self.request)
                self.output = self.guest.output


        def lograw(self):
            item_doc = {
                'data': self.request,
                'connection': self.IP,
                'timestamp': datetime.now(),
                'type': self.request[0]
            }
            db.lograw.insert_one(item_doc)


# BLOCK functional classes

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
        self.workstart = "9:00"
        self.workend = "18:00"
        self.holidays = [5, 6]

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
        result = db.guest.find_one({"verification": self.verification})
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
                    if self.workstart:
                        pass
                    else:
                        self.workstart = "9:00"
                        self.workend = "18:00"
                        self.holidays = [5, 6]
                print()
                print("Our new user data is: ")
                pprint(self.__dict__)
                print()
                if self.duplicates():
                    print("No duplicate was found")
                    db.user.delete_many({"ID": self.ID})
                    print("Deleted old data about user, merging new data")
                    db.user.insert_one(self.__dict__)
                    print("New data is pushed")
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
        print("Finished scanning")
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

    def guestaccess(self, doors, ttl):
        print()
        print()
        print("Given doors are: ")
        pprint(doors)
        print("Given ttl is: " + ttl)
        print()
        print("User ID is: " + self.ID)
        result = db.user.find_one({"ID": self.ID})
        if result:
            print("Found user to give him new accesses: ")
            print(self.ID)
            self.scan_user(result)
            olddoors = result["doors"]
            if olddoors:
                self.doors = olddoors.extend(doors)
            else:
                self.doors = doors
            oldttls = result["ttl"]
            ttls = [ttl] * len(doors)
            if oldttls:
                self.ttl = oldttls.extend(ttls)
            else:
                self.ttl = ttls
            print()
            print("New doors list is: ")
            pprint(self.doors)
            print()
            print("New ttls list is: ")
            pprint(self.ttl)
            print()

            db.user.delete_many({"ID": self.ID})
            db.user.insert_one(self.__dict__)

            print("User is updated: ")
            pprint(self.__dict__)
            print()

            self.generateoutput()
        else:
            print("No one found: ")
            self.output = "r/!"
            print("Output is: " + self.output)
            print("############################")
            return 0


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
        self.pending = None
        self.exist = None

    def analyze(self, ID):
        self.ID = ID
        result = db.door.find_one({"ID": self.ID})
        if result:
            self.name = result["name"]
            self.parent_ID = result["parent_ID"]
            self.parent_zone_ID = result["parent_zone_ID"]
            self.picture = result["picture"]
            self.password = result["password"]
            self.created = result["created"]
            self.creation = result["creation"]
            self.contractor = result["contractor"]
            self.pending = result["pending"]
            self.exist = True
        else:
            self.exist = False


class Access:
    # TODO create user log function to analytics
    def __init__(self):
        self.MAC = None
        self.user_id = None
        self.password = None
        self.ttl = None
        self.output = None
        self.IP = None

    def check(self, request, IP):
        command = request[2]
        self.IP = IP
        if command == "*":
            item_doc = {
                'ID': secrets.token_hex(32),
                "log": datetime.now(),
                "status": "Preaction",
                'error': False,
                'user': request[2::].split(";")[0],
                'door': request[2::].split(";")[1],
                'ip': IP
            }
            db.log.insert_one(item_doc)
            self.output = "a/"
        elif command == "!":
            item_doc = {
                'ID': secrets.token_hex(32),
                "log": datetime.fromtimestamp(float(request[2::].split(";")[2])),
                "status": "Opendoor",
                'error': False,
                'user': request[2::].split(";")[0],
                'door': request[2::].split(";")[1],
                'ip': IP
            }
            db.log.insert_one(item_doc)
            self.output = "a/"
        elif command == "?":
            self.giveaccess(request)
        else:
            self.output = "a/"

    def giveaccess(self, request):
        self.user_id = request[2::].split(";")[0]
        self.MAC = request[2::].split(";")[1]
        result = db.user.find_one({"ID": self.user_id})
        if result:
            macs = result["doors"]
            ttls = result["ttl"]
            for i in range(len(macs)):
                mac = macs[i]
                if mac == self.MAC:
                    self.ttl = ttls[i]
                    door = db.door.find_one({"ID": self.MAC})
                    if door:
                        self.password = door["password"]
                        break
            if self.password:
                self.output = "a/" + str(self.password) + ";" + str(self.ttl) + ";"
        if self.output:
            pass
        else:
            self.output = "a/0;0;"
            item_doc = {
                'ID': secrets.token_hex(32),
                "log": datetime.now(),
                "status": "Failed",
                'error': False,
                'user': request[2::].split(";")[0],
                'door': request[2::].split(";")[1],
                'ip': self.IP
            }
            db.log.insert_one(item_doc)


class Message:
    def __init__(self):
        self.MID = None
        self.ID = None
        self.type = None
        self.icon = None
        self.title = None
        self.text = None
        self.color = None
        self.sent = None
        self.creation = None
        self.created = None
        self.output = None

    def analyze(self, ID):
        results = db.message.find({"$and": [{"ID": ID}, {"sent": False}]})
        if results:
            output = ""
            for result in results:
                self.MID = result["MID"]
                self.ID = ID
                self.type = result["type"]
                self.icon = result["icon"]
                self.title = result["title"]
                self.text = result["text"]
                self.color = result["color"]
                self.sent = True
                self.created = result["created"]
                self.creation = result["creation"]
                self.output = "m/" + self.icon + ";" + self.title + ";" + self.color + ";" + self.text + ";"
                db.message.delete_many({"MID": self.MID})
                db.message.insert_one(self.__dict__)
                output += self.output
        userup = self.updateuser(ID)
        self.output = output + userup

    def updateuser(self, ID):
        result = db.updating.find_one({"$and": [{"ID": ID}, {"pending": False}, {"updated": False}]})
        if result:
            user = User()
            user.verification = result["verification"]
            user.verify()
            result["updated"] = True
            db.updating.delete_many({"UPID": result["UPID"]})
            db.updating.insert_one(result)
            return str(user.output)
        else:
            return ""


class Guest:
    def __init__(self):
        self.ID = None
        self.ttl = None
        self.guestlink = None
        self.doors = None
        self.creation = None
        self.created = None
        self.output = None

    def giveaccess(self, request):
        command = request[2]
        if command == "?":
            self.register(request)
        elif command == "!":
            self.addaccess(request)

    def register(self, request):
        self.ID = secrets.token_hex(32)
        self.created = request[2::].split(";")[0]
        self.ttl = request[2::].split(";")[2]
        self.creation = datetime.now()
        buildings = literal_eval(request[2::].split(";")[1])
        self.doors = []
        # TODO: in future create function that will analyze ttl of given guest links.
        for building in buildings:
            for door in building["enter"]:
                self.doors.append(door["MAC"])
        while True:
            self.guestlink = secrets.token_urlsafe(16)
            result = db.guest.find_one({"guestlink": self.guestlink})
            if result:
                continue
            else:
                break
        self.output = "g/" + self.guestlink
        db.guest.insert_one(self.__dict__)

    def addaccess(self, request):
        user_id = request.split("!")[1].split(";")[0]
        print("User ID in add access method is: " + str(user_id))
        verification = request.split(";")[1]
        print("Created user object")
        print("###########################")
        user = User()
        user.ID = user_id

        self.doors = db.guest.find_one({"guestlink": verification})["doors"]
        self.ttl = db.guest.find_one({"guestlink": verification})["ttl"]

        print("Giving access to doors: ")
        pprint(self.doors)
        print("Giving access by ttl: ")
        pprint(self.ttl)
        user.guestaccess(self.doors, self.ttl)
        self.output = user.output


# BLOCK MAIN


if __name__ == '__main__':
    TCPserver()

