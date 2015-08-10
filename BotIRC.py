#!/usr/bin/python3.4

import socket
from select import select
from threading import Thread
from hashlib import sha256
import json
import os
import string

class server(Thread):
	def __init__(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.config = json.load(open("config.json","r"))
		self.auth = json.load(open("auth.json","r"))
		self.users = {} #{Julien008:channels:{#Dev:{mode:+o}}}
		Thread.__init__(self)

	def send(self, cmd):
		print(">>> " + cmd)
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
			print(motd)
			if motd.count("Current Global"):
				break

		self.send("OPER Bot " + self.config["oper_password"])
		print(self.server.recv(1024).decode())

		for channel in self.config["channels"]:
			self.send("JOIN " + channel)
			names = self.server.recv(1024).decode()
			print(names)

			names = names.split("\r\n")[1]
			for user in names.replace(":","").split(" ")[5:len(names.split(" "))]:
				nick = user.replace("@","").replace("+","")
				if not nick in self.users:
					self.users[nick] = {"Authentificated":False, "channels":[]}

				if user.startswith("@"):
					self.users[nick]["channels"].append(names.split(" ")[4])
					if nick in self.auth:
						if names.split(" ")[4] not in self.auth[nick]["channels"]:
							self.auth[nick]["channels"].append(names.split(" ")[4])

		for channel in self.config["channels"]:
			self.send("SAMode {} +o {}".format(channel, self.config["name"]))



		self.running = True
		while self.running:
			rlist, wlist, xlist = select([self.server], [], [], 0.1)
			if rlist:
				message = self.server.recv(1024).decode()
				if message.count("PRIVMSG " + self.config["name"]) == 0:
					print(message[:-1])

				lines = message.split("\r\n")
				for line in lines:
					args = line.split(" ")

					#Ping
					if len(args) >= 1 and args[0] == "PING":
						self.send("PONG " + args[1])

					#PrivMSG
					elif len(args) >= 4 and args[1] == "PRIVMSG":
						sender = line[1:line.find("!")]

						#PrivateMessage
						if args[2] == self.config["name"]:

							#Register
							if args[3][1:].lower() == "register":
								if sender not in self.auth:
									if len(args) >= 5:
										if 20 >= len(args[4]) >= 8 and set(args[4]) <= set(string.ascii_lowercase + string.digits + '.'):
											self.auth[sender] = {}
											self.auth[sender]["password"] = sha256(args[4].encode()).hexdigest()
											self.auth[sender]["channels-op"] = self.users[sender]["channels"].copy()
											self.send("PRIVMSG {0} Le compte {0} a été enregistré avec le mot de passe {1}. Ce hash sera recalculé à chaque connexion permettant ainsi la protection de vos données.".format(sender, sha256(args[4].encode()).hexdigest()))
										else:
											self.send("PRIVMSG {} ERREUR: Le mot de passe doit être compris entre 8 et 20 caractère et être constitué uniquement de chiffre et de lettre")
									else:
										self.send("PRIVMSG {} ERREUR: Vous devez entrer un mot de passe".format(sender))
								else:
									self.send("PRIVMSG {} ERRER: Vous êtes déjà enregistré. Merci de vous connecter via la commande /msg {} login votre_mot_de_passe".format(sender, self.config["name"]))

							#Login
							elif args[3][1:].lower() == "login":
								if sender in self.auth:
									if len(args) >= 5:
										if self.auth[sender]["password"] == sha256(args[4].encode()).hexdigest():
											self.users[sender]["Authentificated"] = True
											self.send("PRIVMSG {} Vous êtes maintenant connecté".format(sender))
											if "fail" in self.auth[sender]:
												for user in self.auth[sender]["fail"]:
													self.server.send("PRIVMSG {} {} a tenté de se connecter {} fois sur votre compte".format(sender, user, self.auth[sender]["fail"][user]))
													del self.auth.fail[user]
											for channel in self.config["channels"]:
												if channel in self.auth[sender]["channels-op"]:
													self.send("MODE {} +o {}".format(channel, sender))
												else:
													self.send("MODE {} +v {}".format(channel, sender))
										else:
											user = args[0][args[0].find("!")+1:args[0].find("@")]
											host = args[0][args[0].find("@")+1:]

											if not "fail" in self.auth(sender):
												self.auth.fail[user+"@"+host] = 1
											else:
												self.auth.fail[user+"@"+host] += 1

												if host != "localhost" and host != "127.0.0.1":
													if len(self.config["auth_fail"]) > self.auth.fail[user+"@"+host]:
														if self.config["auth_fail"][self.auth.fail[user+"@"+host]]:
															self.send(self.config["auth_fail"][self.auth.fail[user+"@"+host]].format(host=host, user=user, nick=sender))
													else:
														if self.config["auth_fail"][len(self.config["auth_fail"])-1]:
															self.send(self.config["auth_fail"][len(self.config["auth_fail"])-1].format(host=host, user=user, nick=sender))
											self.send("PRIVMSG {} ERREUR: Le mot de passe est incorrecte (Tentative #{})".format(self.auth.fail[args[0][args[0].find("!")+1:]]))
									else:
										self.send("PRIVMSG {} ERREUR: Vous devez entrer un mot de passe".format(sender))
								else:
									self.send("PRIVMSG {} ERRER: Vous n'est pas encore enregistré. Merci de vous enregistrer via la commande /msg {} register votre_mot_de_passe".format(sender, self.config["name"]))
							
							#islogged
							elif args[3][1:].lower() == "islogged":
								if len(args) >= 5 and args[4] in self.users and self.users[args[4]]["Authentificated"] == True:
									self.send("PRIVMSG {} {} est authentifié")
								else:
									self.send("PRIVMSG {} {} n'est pas authentifié")

							else:
								pass

						#PublicMessage
						else:
							pass

					#Join
					elif len(args) >= 3 and args[1] == "JOIN" and line[1:line.find("!")] != self.config["name"]:
						sender = line[1:line.find("!")]
						if sender not in self.users:
							self.users[sender] = {"Authentificated":False, "channels":[args[2][1:].split(",")]}

						if self.users[sender]["Authentificated"] == True:
							for channel in args[2][1:].split(","):
								if channel in self.auth[sender]["channels"]:
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
Bot.start()

while True:
	msg = input()
	if msg == "stop":
		Bot.save()
		Bot.stop()
		break
	else:
		eval(msg)
