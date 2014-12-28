import socket
import sys
import hashlib
import json
import tools
import os
import pickle

def SendCommand(command):
	"""Send a command on the IRC serveur"""
	tools.log(command, "SERVER")
	server.send((command + "\r\n").encode())

def SendMessage(target, message):
	"""Send a message to a target (client/channel) on the IRC serveur"""
	tools.log(target + ": " + message, "MSG")
	server.send(("PRIVMSG " + target + " " + message + "\r\n").encode())

def GetMessage(linex, index):

	i = int(0)
	message = str("")
	while i < len(linex):
		if i == index:
			if linex[i].startswith(":"):
				message = linex[i][1:]
			else:
				message = linex[i]
		elif i > index:
			message += " " + linex[i]
		i+=1
	return message

def GetSender(linex):
	"""Get the sender of an IRC message by parsing the command"""
	return linex[0][1:linex[0].find("!")]

def GetData(key):
	"""Return a data stored"""
	return data[key]

def GetMode(channel, user):
	"""Get the mode of the given user in the given channel"""
	for client in data[("clients",channel)]:
		if client[1:] == user or client == user:
			tools.log("Found " + client)

			if client.startswith("@"):
				return (1,"OP","+o")

			elif client.startswith("%"):
				return (2,"HALF-OP","+h")

			elif client.startswith("+"):
				return (3,"VOICE","+v")

			else:
				return (4,"USER", "-v")
	tools.log(user + " not found !", "WARNING")
	return (5, user + " not found !", "-h")

def GetNameWithoutPrefix(user):
	if user.startswith("+") or user.startswith("%") or user.startswith("@"):
		return user[1:]
	else:
		return user

#Public Variables
trad = tools.traduction("lang/main.json")
data = {}
server = socket.socket()
auth = {}

tools.log("Loading configuration file.")
try:
	with open("config.json","r") as json_data:
		data = json.load(json_data)
	for channel in data["channels"]:
		auth[channel] = {}

except IOError:
	tools.log(trad.lang["Connection"]["NoConfigurationFileFound"],"WARNING")
	tools.log(trad.lang["Connection"]["MakeANewConfiguration"])
	Host = tools.ask(trad.lang["Connection"]["Host"],"")
	Port = tools.ask(trad.lang["Connection"]["Port"],1)
	Botname = tools.ask(trad.lang["Connection"]["Botname"],"")

	Channels = list()
	Shoutboxes = list()
	n = 0
	while True:
		n+=1
		channel = tools.ask(trad.lang["Connection"]["Channel"] % (n),"")
		shoutbox = tools.ask(trad.lang["Connection"]["Shoutbox"], True)
		if channel != "":
			Channels.append(channel)
			Shoutboxes.append((channel, shoutbox))
		else:
			del n, channel
			break

	Password = tools.ask(trad.lang["Connection"]["Password"],"")

	data = json.dumps(
		{  
			"host":Host,
			"port":Port,
			"botname":Botname,
			"password":Password,
			"channels":Channels,
			"shoutbox":Shoutboxes
		}
	)
	with open("config.json","w") as f:
		f.write(data)

	del Host, Port, Botname, Channels, Password

tools.log("Loading authentification file.")
try:
	with open("auth.json","r") as json_data:
		auth = json.load(json_data)

except FileNotFoundError: tools.log("No Authentification file found.","WARNING")

tools.log(trad.lang["Connection"]["Establishing"] % (data["host"], data["port"]))
server.connect((data["host"], data["port"]))
server.recv(1024).decode()
tools.log(trad.lang["Connection"]["Established"])
tools.log(trad.lang["Connection"]["Connecting"] % (data["botname"]))
server.send(("USER %s %s %s: Bot \r\n" % (data["botname"], data["botname"], data["botname"])).encode("UTF-8"))
server.send(("NICK " + data["botname"] + "\r\n").encode("UTF-8"))
tools.log(trad.lang["Connection"]["WaitPing"] % (", ".join(data["channels"])))

while True:
	recv = server.recv(1024).decode("UTF-8")
	if recv.startswith("PING"):
		tools.log(recv.replace("\r\n",""), "SERVER")
		linex = recv.split()
		SendCommand("PONG " + linex[1][1:])
		break

SendCommand("OPER Bot %s" % data["password"])
for channel in data["channels"]:
	SendCommand("JOIN " + channel)


#Main Core
running = True
while running:

	#Receiving messages from the serveur
	recv = server.recv(4098).decode("UTF-8")

	#Var used for parsing the /NAMES list
	b = bool()
	clients = str()

	#For each line in the message, we shearch for commands
	for line in recv.split("\r\n"):
		linex = line.rstrip()
		linex = linex.split()

		#NAMES LIST PARSING
		if b == True and len(linex) >= 5 and GetMessage(linex, 4) != "End of /NAMES list.":
			if linex[4] != "#opers":
				clients = GetMessage(linex, 5)
				data[("clients",linex[4])] = clients.split(" ")
				for client in clients.split(" "):
					try:
						auth[linex[4]][GetNameWithoutPrefix(client)]
					except KeyError:
						tools.log("+" + GetNameWithoutPrefix(client))
						auth[linex[4]][GetNameWithoutPrefix(client)] = []
		elif b == True and len(linex) >= 5 and GetMessage(linex, 4) == "End of /NAMES list.":
			b = False

		#Ping
		if len(linex) > 1 and linex[0] == "PING":
			SendCommand("PONG " + linex[1][1:].replace("\r\n",""))

		#Join
		elif len(linex) >= 2 and linex[1] == "JOIN":
			if linex[2][1:] != "#opers":
				if linex[0].startswith(":"+data["botname"]):
					b = True
				else:
					channel = linex[2][1:]
					client = GetSender(linex)
					data[("clients",channel)].append(client)
					try:
						auth[channel][GetNameWithoutPrefix(client)]
					except KeyError:
						tools.log("+" + GetNameWithoutPrefix(client))
						auth[linex[4]][GetNameWithoutPrefix(client)] = []
					SendMessage(channel, "Bonjour " + GetNameWithoutPrefix(client))

		#Part
		elif len(linex) >= 3 and linex[1] == "PART":
			data[("clients",linex[2])].remove(GetSender(linex))

		#Privmsg
		elif len(linex) >= 4 and linex[1] == "PRIVMSG":
			sender = GetSender(linex)
			message = GetMessage(linex, 3).replace("\r\n","")
			commande = message.split(" ")

			#Private message with the bot
			if linex[2] == data["botname"]:

				#Stop
				if commande[0] == "stop".casefold():
					for channel in data["channels"]:
						if GetMode(channel, sender)[0] <= 1:
							for channel in data["channels"]:
								SendCommand("PART " + channel + " " + trad.lang["Bot"]["Quit"])
							running = False
							break
					if running: SendMessage(sender, trad.lang["Bot"]["PermissionDenied"])

				#Auth
				if commande[0] == "auth".casefold() or commande[0] == "identify".casefold():
					if len(commande) == 2:
						try:
							for channel in data["channels"]:
								if auth[channel][sender][1] == hashlib.sha1(commande[1].encode()).hexdigest():
									SendCommand("Mode %s %s %s" % (channel, auth[channel][sender][0], sender))
								else:
									SendMessage(sender, "Wrong password !")
						except KeyError:
							tools.log(sender + " isn't in the user list !", "WARNING")
							SendMessage(sender, "Internal Error !")
							for channel in data["channels"]:
								SendCommand("NAMES " + channel)

						except IndexError:
							for channel in data["channels"]:
								auth[channel][sender] = [GetMode(channel, sender)[2], hashlib.sha1(commande[1].encode()).hexdigest()]
							
							with open("auth.json", "w")	as file:
								file.write(json.dumps(auth))

					else:
						SendMessage(sender, trad.lang["Bot"]["ModeCommandUsage"] % data[botname])

				else:
					tools.log(linex[2] + " " + sender + ": " + message, "MSG")

			#Channel message
			elif linex[2].startswith("#"):
				tools.log(linex[2] + " " + sender + ": " + message, "MSG")

				
		#Kick
		elif len(linex) >= 4 and linex[1] == "KICK":
			data[("clients",linex[2])].remove(linex[3])

		#Mode
		elif len(linex) >= 5 and linex[1] == "MODE":
			tools.log(line, "SERVER")
			tools.log("Updating clients mode")
			SendCommand("NAMES " + linex[2])

		#If it's none of the command above, just print the message into the terminal
		else:
			if line!="":
				tools.log(line, "SERVER")
