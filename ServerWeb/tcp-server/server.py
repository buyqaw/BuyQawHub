#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Bauyrzhan Ospan"
__copyright__ = "Copyright 2019, Buyqaw LLP"
__version__ = "1.0.1"
__maintainer__ = "Bauyrzhan Ospan"
__email__ = "bospan@cleverest.tech"
__status__ = "Development"

# standard import of os
import os
import random
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


# global variables
print_lock = threading.Lock()
client = MongoClient('mongodb://database:27017/')
db = client.buyqaw

# classes

# TODO change it to the new way from flask
# class to deal with new user
class Newuser:
    def __init__(self, data):
        # Request from mobile app:
        # r/o;56303h43;930423;[{"name": "Зеленый Квартал", "id": "555444333", "enter": [{"name": "1A"}]}];BIClients
        self.type = data[2]
        self.data = data.split(";")
        self.id = self.data[1]
        self.origin = self.data[-1]
        self.day = int(self.data[2][4:6])
        self.month = int(self.data[2][2:4])
        self.year, self.age = self.defineage()
        self.doors = json.loads(self.data[3])
        self.givepass()
        self.output = "r/" + self.type + ";" + self.id + ";" + \
                      str(self.year)[-2:] + str(self.month) + \
                      str(self.day) + ";" + str(self.doors) + \
                      ";" + str(self.origin)
        self.register()

    def defineage(self): # Определить возраст человека
        iin = self.data[2]
        year = iin[0:2]
        now = datetime.now()
        if int(year) <= int(str(now.year)[-2:]):
            prefix = "20"
        else:
            prefix = "19"
        year = int(prefix + year)
        birthdate = datetime.strptime(str(self.day) + str(self.month) + str(year), '%d%m%Y')
        age = now.year - birthdate.year - ((now.month, now.day) < (birthdate.month, birthdate.day))
        return year, age

    def givepass(self):
        for i in range(len(self.doors)):
            for j in range(len(self.doors[i]["enter"])):
                self.doors[i]["enter"][j]["key"], self.doors[i]["enter"][j]["ttl"], self.doors[i]['enter'][j]["door_id"] = \
                    self.doorbyparent_id(self.doors[i]["id"], self.doors[i]["enter"][j]["name"])

    def register(self):
        self.check()
        item_doc = {
            'type': self.type,
            'ID': self.id,
            'origin': self.origin,
            'bday': self.day,
            'bmonth': self.month,
            'byear': self.year,
            'age': self.age,
            'doors': self.doors
        }
        db.users.insert_one(item_doc)

    def check(self):
        result = db.users.find_one({"ID": self.id})
        if result:
            db.users.delete_many({"ID": self.id})
        else:
            pass

    def doorbyparent_id(self, parent_id, name):
        result = db.doors.find_one({"parent_id": parent_id, "name": name})
        password = result["password"]
        ttl = result["ttl"]
        door_id = result["ID"]
        return password, ttl, door_id


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
        verificationcode = self.rand_passw(12, id)
        item_doc = {
            'ID': id,
            'guestlink': verificationcode,
            'doors': doors
        }
        db.guests.insert_one(item_doc)

        self.output = verificationcode

    def rand_passw(self, s, end):

        # Takes random choices from
        # ascii_letters and digits
        generate_pass = ''.join([random.choice(string.ascii_uppercase +
                                               string.ascii_lowercase +
                                               string.digits)
                                 for n in range(s)])
        generate_pass += str(end)
        return generate_pass

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


# class to deal with new door
class Newdoor:
    def __init__(self, data, days=365):
        # Request from admin`s page is: x/80:e6:50:02:a3:9a;A1;555444333;parent_zone_id
        data = data.split(";")
        self.days = days
        self.id = data[0][2::]
        self.name = data[1]
        self.parent_id = data[2]
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
            'parent_id': self.parent_id
        }
        db.doors.insert_one(item_doc)
        self.output = "x/" + self.id + ";" + self.name + ";" + self.parent_id + ";"

    def check(self):
        result = db.doors.find_one({"ID": self.id})
        if result:
            db.doors.delete_many({"ID": self.id})
        else:
            pass


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
        if self.door == None:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'alarm': "Enemy BuyNode with our algorithm",
                'timestamp': datetime.now()
            }
            db.alarms.insert_one(item_doc)
        elif self.user == None:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'alarm': "Hacker found",
                'timestamp': datetime.now()
            }
            db.alarms.insert_one(item_doc)
        else:
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
        self.output += str(self.password) + ";" + str(self.ttl) + ";"

    def logit(self, request):  # a/!56303h43;80:e6:50:02:a3:9a;1555666261;
        request = request[3:].split(";")
        user_id = request[0]
        door_id = request[1]
        self.when = request[2]

        if user_id != self.user_id or door_id != self.door_id:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'alarm': "Ids changed",
                'timestamp': datetime.now()
            }
            db.alarms.insert_one(item_doc)
            return ("a/!Donothackme")
        else:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'timestamp': datetime.fromtimestamp(int(self.when))
            }
            db.log.insert_one(item_doc)
            return ("a/!")


class Request:
    def __init__(self, data, connection):
        self.data = data
        self.connection = connection
        self.output = ""
        if self.data[0] == "r" or self.data[0] == "v":
            info = User(data)
        elif self.data[0] == "x":
            info = Newdoor(data)
        elif self.data[0] == "a":
            info = Access(data)
        elif self.data[0] == "g":
            info = Guest(data)

        self.output = info.output
        self.connection.send(str(self.output).encode('utf-8'))

        # TODO add function to log every single peace of action


# functions

# thread function
def threaded(connection):
    while True:

        # data received from client
        data = connection.recv(50000).decode('utf-8')
        if not data:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break

        Request(data, connection)

        # connection closed
    connection.close()


def main():
    host = "0.0.0.0"

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 7777
    sox = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sox.bind((host, port))
    print("socket binded to post", port)

    # put the socket into listening mode
    sox.listen(50)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        connection, addr = sox.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (connection,))
    sox.close()


if __name__ == '__main__':
    main()

