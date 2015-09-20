#!/usr/bin/python3.4

from bs4 import BeautifulSoup
from hashlib import sha256
import json
import re
from select import select
import socket
from threading import Thread
import time
import urllib.request
from os import listdir, getcwd
from os.path import join as pathjoin
from shutil import copyfile

class server(Thread):
	def __init__(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.config = json.load(open("config.json","r"))
		self.auth = json.load(open("auth.json","r"))
		self.users = {}
		self.password_regex = re.compile(self.config["password_regex"])
		self.url_regex =  re.compile("(http(s)?://)?([A-Za-z0-9\-_%]{1,}\.)?[A-Za-z0-9\-_%]{1,}\.(aero|biz|com|coop|edu|info|int|net|org|mil|museum|name|pro|gov|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cx|cy|cz|de|dk|dj|dm|do|dz|ec|ee|eg|eh|er|es|et|fi|fj|fk|fm|fo|fr|fx|ga|gd|ge|gf|gg|gh|gi|gl|gn|gp|gq|gr|gs|gt|gu|gy|hk|hm|hn|hr|ht|hu|id|ie|il|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mx|mw|my|mz|na|nc|nf|ne|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|ph|pk|pl|pm|pn|pq|pr|pt|py|pw|qa|re|ro|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|sv|sy|sz|tc|td|tf|th|tj|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zr|zm|zw)([A-Za-z0-9\-/_%\.]{0,})?")
		self.ip_regex = re.compile("(http(s)?://)?([0-9]{1,3}\.){3}[0-9]{1,3}(/[A-Za-z0-9\-/_%\.]{0,})?")
		Thread.__init__(self)

	def log(self, msg):
		if msg != "":
			if msg.endswith("\n"): msg=msg[:-1]
			print("{} {}{}".format(time.strftime("%x-%X"), "<<< " if not msg.startswith(">>>") else "", msg))
			with open("server.log", "a") as file: file.write("{} {}{}\n".format(time.strftime("%x-%X"), "<<< " if not msg.startswith(">>>") else "", msg))

	def send(self, cmd):
		self.log(">>> " + cmd)
		self.server.send((cmd + "\r\n").encode("UTF-8"))

	def sendToIA(self, channel, msg):
		try:
			if channel not in self.users:
				self.users[channel] = {"Authentificated":False, "channels":[]}
			if "LymOS" not in self.users[channel]:
				self.users[channel]["LymOS"] = {}
				content = BeautifulSoup(urllib.request.urlopen("http://system.lymdun.fr/ls/index.php").read().decode(), "html.parser")
				for t in ["var", "vartemp", "cerveau", "vraiesvars", "nom", "noreut", "vraiesvars", "rappel"]:
					self.users[channel]["LymOS"][t] = content.find(id=t)["value"]

			self.users[channel]["LymOS"]["usersay"] = msg.replace(self.config["name"], "LymOS")
			content = BeautifulSoup(urllib.request.urlopen("http://system.lymdun.fr/ls/index.php", data=urllib.parse.urlencode(self.users[channel]["LymOS"]).encode()).read().decode(), "html.parser")
			for t in ["var", "vartemp", "cerveau", "vraiesvars", "nom", "noreut", "vraiesvars", "rappel"]:
				self.users[channel]["LymOS"][t] = content.find(id=t)["value"]

			answer = content.find(id="reponse_ia").getText()
			if answer.count("le LymOS"): answer = answer.replace("le LymOS", self.config["name"] + " (LymOS: http://system.lymdun.fr/ls/)")
			self.send("PRIVMSG {} :{}".format(channel, answer if answer else "..."))
		except Exception as ex:
			self.send("PRIVMSG {} :IA Temporairement indisponible ({})".format(channel, str(ex)))

	def run(self):
		self.server.connect((self.config["host"], self.config["port"]))
		if self.config["server_password"]:
			self.send("PASS " + self.config["server_password"])
		self.send("NICK " + self.config["name"])
		self.send("USER {} 0 * :Bot IRC servant un service".format(self.config["name"]))

		#On attend la fin du message du jour
		while True:
			motd = self.server.recv(1024).decode()
			[self.log(motd) for motd in motd.split("\r\n")]
			if motd.count("Current Global"):
				break

		for channel in self.config["channels"]:
			self.send("JOIN " + channel)

		if self.config["oper_password"]:
			self.send("OPER Bot " + self.config["oper_password"])
			[self.log(msg) for msg in self.server.recv(1024).decode().split("\r\n")]
			for channel in self.config["channels"]:
				self.send("SAMode {} +o {}".format(channel, self.config["name"]))

		self.running = True
		while self.running:
			rlist, wlist, xlist = select([self.server], [], [], 0.1)
			if rlist:
				try:
					message = self.server.recv(1024).decode()
				except Exception as ex:
					print("ex")
				else:
					lines = message.split("\r\n")
					for line in lines:
						args = line.split(" ")

						if line.count("PRIVMSG " + self.config["name"]) == 0:
							self.log(line)

						#Ping
						if len(args) >= 1 and args[0] == "PING":
							self.send("PONG " + args[1])

						#PrivMSG
						elif len(args) >= 4 and args[1] == "PRIVMSG":
							sender = line[1:line.find("!")]
							args[3] = args[3][1:]

							#PrivateMessage
							if args[2] == self.config["name"]:

								#register <password>
								if args[3].lower() == "register":
									self.log(" ".join(args[0:4]))
									if sender not in self.auth:
										if len(args) >= 5:
											if self.password_regex.search(args[4]):
												self.auth[sender] = {}
												self.auth[sender]["password"] = sha256(args[4].encode()).hexdigest()
												self.auth[sender]["channels"] = {}
												for channel in self.config["channels"]:
													self.auth[sender]["channels"][channel] = "+v"
												self.send("PRIVMSG {0} Le compte {0} a été enregistré avec le hash {1}. Ce hash est calculé à partir de votre mot de passe permettant ainsi la protection de vos données.".format(sender, sha256(args[4].encode()).hexdigest()))
												self.send("PRIVMSG {} Vous êtes maintenant connecté".format(sender))
												for channel in self.config["channels"]:
													self.send("MODE {} {} {}".format(channel, self.auth[sender]["channels"][channel], sender))
											else:
												self.send("PRIVMSG {} ERREUR: Le mot de passe doit avoir au moins 8 caractères et être constitué uniquement de chiffre et de lettre (REGEX: {})".format(sender, self.config["password_regex"]))
										else:
											self.send("PRIVMSG {} ERREUR: Vous devez entrer un mot de passe".format(sender))
									else:
										self.send("PRIVMSG {} ERRER: Vous êtes déjà enregistré. Merci de vous connecter via la commande /msg {} login votre_mot_de_passe".format(sender, self.config["name"]))

								#Login <password>
								elif args[3].lower() == "login":
									self.log(" ".join(args[0:4]))
									if sender in self.auth:
										if len(args) >= 5:
											if self.auth[sender]["password"] == sha256(args[4].encode()).hexdigest():
												if sender in self.users:
													self.users[sender]["Authentificated"] = True
												else:
													self.users[sender] = {"Authentificated":True, "channels":[]}

												self.send("PRIVMSG {} Vous êtes maintenant connecté".format(sender))
												if "fail" in self.auth[sender]:
													for user in self.auth[sender]["fail"]:
														self.send("PRIVMSG {} {} a tenté de se connecter {} fois sur votre compte".format(sender, user, self.auth[sender]["fail"][user]))
													del self.auth[sender]["fail"]
												for channel in self.config["channels"]:
													if channel not in self.auth[sender]["channels"]:
														self.auth[sender]["channels"][channel] = "+v"
													self.send("MODE {} {} {}".format(channel, self.auth[sender]["channels"][channel], sender))
											else:
												user = args[0][args[0].find("!")+1:args[0].find("@")]
												host = args[0][args[0].find("@")+1:]

												if not "fail" in self.auth[sender]:
													self.auth[sender]["fail"] = {}
													self.auth[sender]["fail"][user+"@"+host] = 1
												else:
													if user+"@"+host in self.auth[sender]["fail"]:
														self.auth[sender]["fail"][user+"@"+host] += 1
													else:
														self.auth[sender]["fail"][user+"@"+host] = 1

													if host != "localhost" and host != "127.0.0.1":
														if len(self.config["auth_fail"]) > self.auth[sender]["fail"][user+"@"+host]:
															if self.config["auth_fail"][self.auth[sender]["fail"][user+"@"+host]-2]:
																self.send(self.config["auth_fail"][self.auth[sender]["fail"][user+"@"+host]].format(host=host, user=user, nick=sender))
														else:
															if self.config["auth_fail"][len(self.config["auth_fail"])-1]:
																self.send(self.config["auth_fail"][len(self.config["auth_fail"])-1].format(host=host, user=user, nick=sender))
													elif user == "webchat":
														self.send("KILL {nick} Mot de passe incorrect sur l'interface web".format(host=host, user=user, nick=sender))
												self.send("PRIVMSG {} ERREUR: Le mot de passe est incorrect (Tentative #{})".format(sender, self.auth[sender]["fail"][user+"@"+host]))
										else:
											self.send("PRIVMSG {} ERREUR: Vous devez entrer un mot de passe".format(sender))
									else:
										self.send("PRIVMSG {} ERREUR: Vous n'est pas encore enregistré. Merci de vous enregistrer via la commande /msg {} register votre_mot_de_passe".format(sender, self.config["name"]))

								#ghost <nickname> <password>
								elif args[3].lower() == "ghost":
									self.log(" ".join(args[0:5]))
									if len(args) >= 6:
										username = args[4]
										password = args[5]
										if username in self.auth:
											if self.auth[username]["password"] == sha256(password.encode()).hexdigest():
												self.send("KILL {} Ghost".format(username))
												self.send("SANICK {} {}".format(sender, username))
												if username in self.users:
													self.users[username]["Authentificated"] = True
												else:
													self.users[username] = {"Authentificated":True, "channels":[]}

												self.send("PRIVMSG {} Vous êtes maintenant connecté".format(username))
												if "fail" in self.auth[username]:
													for user in self.auth[username]["fail"]:
														self.send("PRIVMSG {} {} a tenté de se connecter {} fois sur votre compte".format(username, user, self.auth[username]["fail"][user]))
													del self.auth[username]["fail"]
												for channel in self.config["channels"]:
													if channel not in self.auth[username]["channels"]:
														self.auth[username]["channels"][channel] = "+v"
													self.send("MODE {} {} {}".format(channel, self.auth[username]["channels"][channel], username))
											else:
												user = args[0][args[0].find("!")+1:args[0].find("@")]
												host = args[0][args[0].find("@")+1:]

												if not "fail" in self.auth[username]:
													self.auth[username]["fail"] = {}
													self.auth[username]["fail"][user+"@"+host] = 1
												else:
													if user+"@"+host in self.auth[username]["fail"]:
														self.auth[username]["fail"][user+"@"+host] += 1
													else:
														self.auth[username]["fail"][user+"@"+host] = 1

													if host != "localhost" and host != "127.0.0.1":
														if len(self.config["auth_fail"]) > self.auth[username]["fail"][user+"@"+host]:
															if self.config["auth_fail"][self.auth[username]["fail"][user+"@"+host]-2]:
																self.send(self.config["auth_fail"][self.auth[username]["fail"][user+"@"+host]].format(host=host, user=user, nick=username))
														else:
															if self.config["auth_fail"][len(self.config["auth_fail"])-1]:
																self.send(self.config["auth_fail"][len(self.config["auth_fail"])-1].format(host=host, user=user, nick=username))
													else:
														self.send("KILL {nick} Mot de passe incorrect sur l'interface web".format(host=host, user=user, nick=username))
												self.send("PRIVMSG {} ERREUR: Le mot de passe est incorrect (Tentative #{})".format(sender, self.auth[username]["fail"][user+"@"+host]))
										else:
											self.send("PRIVMSG {} ERREUR: {} n'est pas enregistré.".format(sender, username))
									else:
										self.send("PRIVMSG {} ERREUR: Vous devez entrer un nickname et un mot de passe".format(sender))

								#islogged <nick>
								elif args[3].lower() == "islogged":
									self.log(line)
									self.send("PRIVMSG {} {} {} authentifié".format(sender, args[4], "est" if len(args) >= 5 and args[4] in self.users and self.users[args[4]]["Authentificated"] == True else "n'est pas"))

								#about
								elif args[3].lower() == "about":
									self.log(line)
									msg = "# {} - Bot IRC V3 #".format(self.config["name"])
									self.send("PRIVMSG {} {}".format(sender, "".join(["#" for char in msg])))
									self.send("PRIVMSG {} {}".format(sender, msg))
									self.send("PRIVMSG {} {}".format(sender, "".join(["#" for char in msg])))
									self.send("PRIVMSG {} {} est un bot (programme) développé par Julien Castiaux (Julien008) pour le réseau IRC de la BakaConnect.".format(sender, self.config["name"]))
									self.send("PRIVMSG {} L'intelligence artificielle est basée sur LymOS et est développé par Lymdun".format(sender))
									self.send("PRIVMSG {} README complet: https://github.com/Julien00859/Bot_IRC/blob/master/README.md".format(sender))

								#LymOS
								else:
									if len(args) >= 4:
										self.log(line)
										self.sendToIA(sender, " ".join(args[3:len(args)]))

							#PublicMessage
							else:
								#Message commençant par le nom de notre bot
								if args[3].lower().count(self.config["name"].lower()):
									self.sendToIA(args[2], " ".join(args[4:len(args)]))

								for arg in args[3:len(args)]:
									match = self.url_regex.search(arg) if self.url_regex.search(arg) else self.ip_regex.search(arg)
									if match:
										arg = match.group(0) if match.group(0).startswith("http") else "http://" + match.group(0)
										try:
											self.send("PRIVMSG {} {} [{}]".format(args[2], BeautifulSoup(urllib.request.urlopen(arg).read(), "html.parser").title.getText().replace("\n",""), arg))
										except:
											pass


						#Join
						elif len(args) >= 3 and args[1] == "JOIN" and line[1:line.find("!")] != self.config["name"]:
							sender = line[1:line.find("!")]
							if sender not in self.users:
								self.users[sender] = {"Authentificated":False}

							if self.users[sender]["Authentificated"] == True:
								for channel in args[2][1:].split(","):
									if channel in self.auth[sender]["channels"].keys():
										self.send("MODE {} {} {}".format(channel, self.auth[sender]["channels"][channel], sender))
							else:
								self.send("PRIVMSG {} Le salon {} est un salon officiel qui nécessite une authentification.".format(sender, args[2][1:]))
								if sender in self.auth:
									self.send("PRIVMSG {} Merci de vous connecter via la commande \"/msg {} login votre_mot_de_passe\"".format(sender, self.config["name"]))
								else:
									self.send("PRIVMSG {} Merci de vous enregistrer via la commande \"/msg {} register un_mot_de_passe\"".format(sender, self.config["name"]))

						#Nick
						elif len(args) >= 2 and args[1] == "NICK":
							sender = line[1:line.find("!")]
							if sender in self.users:
								self.users[args[2]] = {"Authentificated": self.users[sender]["Authentificated"]}
								del self.users[sender]

							else:
								self.users[args[2]] = {"Authentificated": False}

						#Quit
						elif len(args) >= 2 and args[1] == "QUIT":
							if line[1:line.find("!")] in self.users:
								del self.users[line[1:line.find("!")]]

	def save(self):
		with open("auth.json","w") as file:
			file.write(json.dumps(self.auth, indent="\t", sort_keys=True))

	def reload(self):
		self.auth = json.load(open("auth.json","r"))

	def stop(self):
		self.send("QUIT :Le vaisseau mère a besoin de moi !")
		self.running = False

if "auth.json" not in listdir():
	copyfile(pathjoin(getcwd(), "template", "auth.json"), pathjoin(getcwd(), "auth.json"))

if "config.json" not in listdir():
	copyfile(pathjoin(getcwd(), "template", "config.json"), pathjoin(getcwd(), "config.json"))

Bot = server()
Bot.log("Starting")
Bot.start()

while True:
	msg = input()
	if msg == "stop":
		Bot.save()
		Bot.stop()
		break
	else:
		try:
			eval(msg)
		except Exception as ex:
			print(ex)
