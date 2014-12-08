import socket
import sys
import threading
import hashlib
import requests
from bs4 import BeautifulSoup
import requests
import time
import json
import tools

def sendcommand(server, command):
    tools.log(command, "SERVER")
    server.send((command + "\r\n").encode())

trad = tools.traduction("lang/main.json")
data = json.dumps({})
try:
    with open("config.json","r") as json_data:
        data = json.load(json_data)
except IOError:
    tools.log(trad.lang["Core"]["NoConfigurationFileFound"])
    tools.log(trad.lang["Core"]["MakeANewConfiguration"])
    Host = tools.ask(trad.lang["Core"]["Host"],"")
    Port = tools.ask(trad.lang["Core"]["Port"],1)
    Botname = tools.ask(trad.lang["Core"]["Botname"],"")

    Channels = list()
    n = 0
    while True:
        n+=1
        channel = tools.ask(trad.lang["Core"]["Channel"] % (n),"")
        if channel != "":
            Channels.append(channel)
        else:
            del n, channel
            break

    Password = hashlib.sha1((tools.ask(trad.lang["Core"]["Password"],"")).encode()).hexdigest()

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

    data = json.load(data)
    del Host, Port, Botname, Channels, Password

server = socket.socket()
tools.log(trad.lang["Core"]["Establishing"] % (data["host"], data["port"]))
server.connect((data["host"], data["port"]))
server.recv(1024).decode()
tools.log(trad.lang["Core"]["Established"])
tools.log(trad.lang["Core"]["Connecting"] % (data["botname"]))
server.send(("USER %s %s %s: Bot \r\n" % (data["botname"], data["botname"], data["botname"])).encode("UTF-8"))
server.send(("NICK " + data["botname"] + "\r\n").encode("UTF-8"))
tools.log(trad.lang["Core"]["WaitPing"] % (", ".join(data["channels"])))

while True:
    recv = server.recv(1024).decode("UTF-8")
    if recv.startswith("PING"):
        tools.log(recv.replace("\r\n",""), "SERVER")
        linex = recv.split()
        sendcommand(server,"PONG " + linex[1][1:])
        break

tools.log("Joining channels")
for channel in data["channels"]:
    sendcommand(server,"JOIN " + channel)