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
        self.ttl = datetime.now().second + self.days*86400
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


class Request:
    def __init__(self, request):  # request in form: a/?56303h43;80:e6:50:02:a3:9a;
        request = request[3:].split(";")
        self.user_id = request[0]
        self.door_id = request[1]
        self.password = "0"
        self.ttl = "0"
        self.user = ''
        self.door = ''
        self.output = "a/"
        self.when = ''
        self.check()

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
            result = db.users.find_one({"doors.enter.door_id": self.door_id})
            if result:
                print("Asked door with id:" + str(self.door_id) +
                      " was found in user`s config by id: " + str(result["ID"]))
                for buildings in result["doors"]:
                    for doors in buildings["enter"]:
                        try:
                            if doors["door_id"] == self.door_id:
                                print("Door`s name is " + str(doors["name"]))
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
            return("a/!Donothackme")
        else:
            item_doc = {
                'user_id': self.user_id,
                'door_id': self.door_id,
                'timestamp': datetime.fromtimestamp(int(self.when))
            }
            db.log.insert_one(item_doc)
            return("a/!")


# functions

# thread function
def threaded(c):
    while True:

        # data received from client
        data = c.recv(50000).decode('utf-8')
        if not data:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break

        if data[0] == "r":
            newuser = Newuser(data)
            c.send(newuser.output.encode('utf-8'))
        elif data[0] == "x":
            newdoor = Newdoor(data)
            c.send(newdoor.output.encode('utf-8'))
        elif data[0] == "a" and data[2] == "?":
            newreq = Request(data)
            c.send(newreq.output.encode('utf-8'))
        elif data[0] == "a" and data[2] == "!":
            try:
                c.send(newreq.logit(data).encode('utf-8'))
            except:
                print("Problem here")

        # connection closed
    c.close()


def Main():
    host = "0.0.0.0"

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 7777
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to post", port)

    # put the socket into listening mode
    s.listen(50)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()


if __name__ == '__main__':
    Main()

