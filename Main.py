import socket
import sys
import threading
import pickle
import hashlib
import requests
from bs4 import BeautifulSoup
import requests
import time
import json
import Tools

trad = Tools.traduction("lang/main.json")
data = json.dumps({})
try:
    with open("config.json","r") as json_data:
        data = json.load(json_data)
except IOError:
    Tools.log(trad["Core"]["NoConfigurationFileFound"])
    Tools.log(trad["Core"]["MakeANewConfiguration"])
    Host = Tools.ask(trad["Core"]["Host"],"")
    Port = Tools.ask(trad["Core"]["Port"],1)
    Botname = Tools.ask(trad["Core"]["Botname"],"")

    Channels = list()
    n = 0
    while True:
        n+=1
        channel = Tools.ask(trad["Core"]["Channel"] % (n),"")
        if channel != "":
            Channels.append(channel)
        else:
            del n, channel
            break

    Password = hashlib.sha1((Tools.ask(trad["Core"]["Password"],"")).encode()).hexdigest()

    data = json.dumps(
        {  
            "host":Host,
            "port":Port,
            "botname":Botname,
            "password":Password,
            "channels":Channels
        }
    )
    with open("config.json","w") as f:
        f.write(data)

    del Host, Port, Botname, Channels, Password

server = socket.socket()
Tools.log(trad["Core"]["Establishing"] % (data["host"], data["port"]))
server.connect((data["host"], data["port"]))
server.recv(1024).decode()
Tools.log(trad["Core"]["Established"])
Tools.log(trad["Core"]["Connecting"] % data["botname"])
server.send(("USER %s %s %s: Bot \r\n" % (data["botname"], data["botname"], data["botname"])).encode("UTF-8"))
server.send(("NICK " + data["botname"] + "\r\n").encode("UTF-8"))
Tools.log(trad["Core"]["Connected"] % (", ".join(data["channels"])))

while True:
    recv = server.recv(1024).decode("UTF-8")
    if recv.startswith("PING"):
        Tools.log(recv.replace("\r\n",""), "SERVER")
        linex = recv.split()
        server.send(("PONG " + linex[1] + "\r\n").encode())
        Tools.log("PONG " + linex[1], "SERVER")
        break