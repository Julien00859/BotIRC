#!/usr/bin/python
# -*- coding: utf-8 -*-

import Skype4Py
import socket
from select import select
import json

def send(socket, msg):
	print(msg)
	socket.send((msg + "\r\n").encode("UTF-8"))

config = json.load(open("config.json","r"))


skype = Skype4Py.Skype()
skype.Attach()
convo = skype.FindChatUsingBlob(config[u"SkypeBlob"])

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((config[u"host"] , config[u"port"]))

send(socket, "NICK %s" % config[u"nickname"])
send(socket, "USER %s 0 * :Bot IRC se liant a Skype" % config[u"nickname"])

while True:
	motd = socket.recv(1024).decode()
	print(motd)
	if "End of message of the day" in motd:
		break
send(socket, "JOIN #Dev")

# === Main ===
while True:
	new_message, wlist, xlist = select([socket], [], [], 0.1)
	if new_message:
		try:
			msg = socket.recv(1024).decode()
		except Exception as ex:
			print(ex)
		else:
			for line in msg.split("\r\n"):
				print(line)
				args = line.split(" ")
				if len(args) >= 2 and args[0] == "PING":
					send(socket, "PONG %s" % args[1])

				elif len(args) >= 4 and args[1] == "PRIVMSG":
					sender = args[0][1:line.find("!")]
					channel = args[2]
					if channel == "#Dev":
						convo.SendMessage("%s: %s" % (sender, " ".join(args[3:len(args)])[1:]))

socket.close()