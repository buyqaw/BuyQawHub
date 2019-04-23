#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Bauyrzhan Ospan"
__copyright__ = "Copyright 2019, Buyqaw LLP"
__version__ = "1.0.1"
__maintainer__ = "Bauyrzhan Ospan"
__email__ = "bospan@cleverest.tech"
__status__ = "Development"

# standard imports for flask server
from gevent import monkey

monkey.patch_all()

import requests
import glob
import os
from flask import Flask, render_template, session, request, json, jsonify, url_for, Markup, redirect
import random
import re
from pprint import pprint
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import random
from flask import Markup
import copy
from werkzeug.utils import secure_filename
import base64
import telepot

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

from flask_basicauth import BasicAuth

# global variables

client = MongoClient('mongodb://database:27017/')
db = client.buyqaw

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = threading.Lock()


app.config['BASIC_AUTH_USERNAME'] = 'cleverest'
app.config['BASIC_AUTH_PASSWORD'] = 'The2ndlaw'

basic_auth = BasicAuth(app)


# classes
class Admin:
    def __init__(self):
        self.admin = "this"


# app routes

# index page
@app.route('/', methods=['POST', 'GET'])  # Вывод на экраны
@basic_auth.required
def glavnaia():
    print("glavnaia")
    if request.method == 'POST':
        print("POST method")
        name = request.form['name']
        id = request.form["ID"]
        mac = request.form["mac"]
        item_doc = {
            'name': name,
            'ID': id,
            'password': "060593",
            'ttl': str(datetime.now().second + 365*86400),
            'parent_id': id
        }
        db.doors.insert_one(item_doc)
    return render_template('add.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8888, debug=True)
