#!/usr/bin/python3.4

from bs4 import BeautifulSoup
from hashlib import sha256
import json
from select import select
import socket
import string
from threading import Thread
import time
import urllib.request
 
class server(Thread):
	def __init__(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.config = json.load(open("config.json","r"))
		self.auth = json.load(open("auth.json","r"))
		self.users = {} #{Julien008:channels:{#Dev:{mode:+o}}}
		Thread.__init__(self)

	def log(self, msg):
		if msg != "":
			if msg.endswith("\n"): msg=msg[:-1]
			print("{} {}{}".format(time.strftime("%x-%X"), "<<< " if not msg.startswith(">>>") else "", msg))
			with open("server.log", "a") as file: file.write("{} {}{}\n".format(time.strftime("%x-%X"), "<<< " if not msg.startswith(">>>") else "", msg))

	def send(self, cmd):
		self.log(">>> " + cmd)
		self.server.send((cmd + "\r\n").encode("UTF-8"))

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

		self.send("OPER Bot " + self.config["oper_password"])
		[self.log(msg) for msg in self.server.recv(1024).decode().split("\r\n")]

		for channel in self.config["channels"]:
			self.send("JOIN " + channel)
			names = self.server.recv(1024).decode()
			[self.log(names) for names in names.split("\r\n")]

			names = names.split("\r\n")[1]
			for user in names.replace(":","").split(" ")[5:len(names.split(" "))]:
				nick = user.replace("@","").replace("+","")
				if not nick in self.users:
					self.users[nick] = {"Authentificated":False, "channels":[]}

				if user.startswith("@"):
					self.users[nick]["channels"].append(names.split(" ")[4])
					if nick in self.auth:
						if names.split(" ")[4] not in self.auth[nick]["channels-op"]:
							self.auth[nick]["channels-op"].append(names.split(" ")[4])

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

							#PrivateMessage
							if args[2] == self.config["name"]:

								#register <password>
								if args[3][1:].lower() == "register":
									self.log(" ".join(args[0:4]))
									if sender not in self.auth:
										if len(args) >= 5:
											if 20 >= len(args[4]) >= 8 and set(args[4]) <= set(string.ascii_lowercase + string.digits + '.'):
												self.auth[sender] = {}
												self.auth[sender]["password"] = sha256(args[4].encode()).hexdigest()
												self.auth[sender]["channels-op"] = self.users[sender]["channels"].copy()
												self.send("PRIVMSG {0} Le compte {0} a été enregistré avec le mot de passe {1}. Ce hash sera recalculé à chaque connexion permettant ainsi la protection de vos données.".format(sender, sha256(args[4].encode()).hexdigest()))
												self.send("PRIVMSG {} Vous êtes maintenant connecté".format(sender))
												for channel in self.config["channels"]:
													self.send("MODE {} +v {}".format(channel, sender))
											else:
												self.send("PRIVMSG {} ERREUR: Le mot de passe doit être compris entre 8 et 20 caractère et être constitué uniquement de chiffre et de lettre".format(sender))
										else:
											self.send("PRIVMSG {} ERREUR: Vous devez entrer un mot de passe".format(sender))
									else:
										self.send("PRIVMSG {} ERRER: Vous êtes déjà enregistré. Merci de vous connecter via la commande /msg {} login votre_mot_de_passe".format(sender, self.config["name"]))

								#Login <password>
								elif args[3][1:].lower() == "login":
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
													if channel in self.auth[sender]["channels-op"]:
														self.send("MODE {} +o {}".format(channel, sender))
													else:
														self.send("MODE {} +v {}".format(channel, sender))
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
														self.send("KILL {nick} Mot de passe incorrecte sur l'interface web".format(host=host, user=user, nick=sender))
												self.send("PRIVMSG {} ERREUR: Le mot de passe est incorrecte (Tentative #{})".format(sender, self.auth[sender]["fail"][user+"@"+host]))
										else:
											self.send("PRIVMSG {} ERREUR: Vous devez entrer un mot de passe".format(sender))
									else:
										self.send("PRIVMSG {} ERRER: Vous n'est pas encore enregistré. Merci de vous enregistrer via la commande /msg {} register votre_mot_de_passe".format(sender, self.config["name"]))
								
								#islogged <nick>
								elif args[3][1:].lower() == "islogged":
									self.log(line)
									if len(args) >= 5 and args[4] in self.users and self.users[args[4]]["Authentificated"] == True:
										self.send("PRIVMSG {} {} est authentifié".format(sender, args[4]))
									else:
										self.send("PRIVMSG {} {} n'est pas authentifié".format(sender, args[4]))

								#about
								elif args[3][1:].lower() == "about":
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
										try:
											if sender not in self.users:
												self.users[sender] = {"Authentificated":False, "channels":[]}
											if "LymOS" not in self.users[sender]:
												self.users[sender]["LymOS"] = {}
												content = BeautifulSoup(urllib.request.urlopen("http://system.lymdun.fr/ls/index.php").read().decode(), "html.parser")
												for t in ["var", "vartemp", "cerveau", "vraiesvars", "nom", "noreut", "vraiesvars", "rappel"]:
													self.users[sender]["LymOS"][t] = content.find(id=t)["value"]
												
											self.users[sender]["LymOS"]["usersay"] = " ".join(args[3:len(args)]).replace(self.config["name"], "LymOS")
											content = BeautifulSoup(urllib.request.urlopen("http://system.lymdun.fr/ls/index.php", data=urllib.parse.urlencode(self.users[sender]["LymOS"]).encode()).read().decode(), "html.parser")
											for t in ["var", "vartemp", "cerveau", "vraiesvars", "nom", "noreut", "vraiesvars", "rappel"]:
												self.users[sender]["LymOS"][t] = content.find(id=t)["value"]

											answer = content.find(id="reponse_ia").getText()
											if answer.count("le LymOS"): answer = answer.replace("le LymOS", self.config["name"] + " (LymOS: http://system.lymdun.fr/ls/)")
											self.send("PRIVMSG {} {}".format(sender, answer if answer else "..."))
										except Exception as ex:
											self.send("PRIVMSG {} IA Temporairement indisponible ({})".format(sender, str(ex)))

							#PublicMessage
							else:
								pass

						#Join
						elif len(args) >= 3 and args[1] == "JOIN" and line[1:line.find("!")] != self.config["name"]:
							sender = line[1:line.find("!")]
							if sender not in self.users:
								self.users[sender] = {"Authentificated":False, "channels":[]}

							if self.users[sender]["Authentificated"] == True:
								for channel in args[2][1:].split(","):
									if channel in self.auth[sender]["channels-op"]:
										self.send("MODE {} +o {}".format(channel, sender))
									else:
										self.send("MODE {} +v {}".format(channel, sender))

							else:
								self.send("PRIVMSG {} Le salon {} est un salon officiel qui nécessite une authentification.".format(sender, args[2][1:]))
								if sender in self.auth:
									self.send("PRIVMSG {} Merci de vous connecter via la commande \"/msg {} login votre_mot_de_passe\"".format(sender, self.config["name"]))
								else:
									self.send("PRIVMSG {} Merci de vous enregistrer via la commande \"/msg {} register un_mot_de_passe\"".format(sender, self.config["name"]))

						#Quit
						elif len(args) >= 2 and args[1] == "QUIT":
							del self.users[line[1:line.find("!")]]

	def save(self):
		with open("auth.json","w") as file:
			file.write(json.dumps(self.auth, indent="\t", sort_keys=True))

	def stop(self):
		self.send("QUIT :Le vaisseau mère a besoin de moi !")
		self.running = False

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
