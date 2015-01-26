#Import
from API import *
import socket

#Publics variales
trad = Traduction("lang.json")
API = IRC_API(socket.socket(), dict())

#Configuration
log(trad.lang["Main"]["Load"]["LoadConf"])
try:
	with open("config.json","r") as jsonData:
		API.data = json.load(jsonData)
		log(trad.lang["Main"]["Load"]["ConfLoaded"])
except IOError:
	log(trad.lang["Main"]["Load"]["NoConfFileFound"],"WARNING")
	API.data["Host"] = ask(trad.lang["Main"]["Load"]["Host"], "")
	API.data["Port"] = ask(trad.lang["Main"]["Load"]["Port"], 1)
	API.data["IRCPassword"] = ask(trad.lang["Main"]["Load"]["IRCPassword"], "")
	API.data["OperPassword"] = ask(trad.lang["Main"]["Load"]["OperPassword"], "")
	API.data["Botname"] = ask(trad.lang["Main"]["Load"]["Botname"], "")
	API.data["Channels"]=[]
	while True:
		Channel = ask(trad.lang["Main"]["Load"]["Channel"], "")
		if Channel != "":
			API.data["Channels"].append(Channel)
		else:
			break
	with open("config.json","w") as file:
		file.write(BeautifulJSON(json.dumps(API.data)))
		log(trad.lang["Main"]["Load"]["ConfSaved"])

#Server Connection
API.server = socket.socket()
log(trad.lang["Main"]["Connection"]["Server"] % (API.data["Host"], API.data["Port"]))
API.server.connect((API.data["Host"], API.data["Port"]))
API.server.recv(1024).decode("UTF-8")

#IRC Connection
log(trad.lang["Main"]["Connection"]["Bot"])
if API.data["IRCPassword"] != "":
	API.SendCommand("PASS %s" % API.data["IRCPassword"])
API.SendCommand("NICK %s" % API.data["Botname"])
API.SendCommand("USER %s 0 * :BotAzagut" % API.data["Botname"])
if API.data["OperPassword"] != "":
	API.SendCommand("OPER %s %s" % [API.data["Botname"], API.data["OperPassword"]])

log(trad.lang["Main"]["Connection"]["Ping"])
while True:
	recv = API.server.recv(1024).decode("UTF-8")
	if recv.startswith("PING"):
		log(recv.replace("\r\n",""), "SERVER")
		linex = recv.split()
		API.SendCommand("PONG " + linex[1][1:])
		break

log(trad.lang["Main"]["Connection"]["Channels"] % ",".join(API.data["Channels"]))
for channel in API.data["Channels"]:
	API.SendCommand("JOIN " + channel)