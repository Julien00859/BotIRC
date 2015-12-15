#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

from importlib import import_module
from os import getcwd
from select import select
import json
import os.path
import socket

class Plugins():
	def __init__(self, api):
		self.API = api

		plugins_path = os.path.join(getcwd(), "plugins")
		if not os.path.exists(plugins_path):
			os.mkdir("plugins")

		self.plugins = []
		for plugin in os.listdir(plugins_path):
			if plugin.endswith(".py") and plugin != "__init__.py":
				self.plugins.append(import_module("plugins." + plugin[:plugin.find(".")]))

	def load(self):
		for plugin in self.plugins:
			if "onLoad" in plugin.__dict__:
				plugin.onLoad(self.API)

	def loop(self):
		for plugin in self.plugins:
			if "onLoop" in plugin.__dict__:
				plugin.onLoop(self.API)

	def privateMessage(self, channel, sender, message):
		for plugin in self.plugins:
			if "onPrivateMessage" in plugin.__dict__:
				plugin.onPrivateMessage(self.API, channel, sender, message)

	def publicMessage(self, channel, sender, message):
		for plugin in self.plugins:
			if "onPublicMessage" in plugin.__dict__:
				plugin.onPublicMessage(self.API, channel, sender, message)

	def join(self, channel, user):
		for plugin in self.plugins:
			if "onJoin" in plugin.__dict__:
				plugin.onJoin(self.API, channel, user)

	def stop(self):
		print("Stopping...")
		for plugin in self.plugins:
			plugin.onStop()


class API():
	def __init__(self, server):
		self._server = server
		self._config = json.load(open("config.json", "r"))

	def stop(self):
		self._server.plugins.stop()
		self._server.running = False

	def sendCommand(self, cmd):
		self._server.socket.send("{}\r\n".format(cmd).encode())

	def sendMessage(self, channel, message):
		self.sendCommand("PRIVMSG {} :{}\r\n".format(channel, message))

	def getNick(self):
		return self._config["nickname"]

	def getChannels(self):
		return self._config["channels"]

class Server():
	def __init__(self):

		self.API = API(self)
		self.plugins = Plugins(self.API)

		with open("config.json", "r") as json_data:
			config = json.load(json_data)
			host = config["host"]
			port = config["port"]
			sleepTime = config["sleepTime"]

		commands = {"PING":self.ping,"PRIVMSG":self.privmsg, "JOIN":self.join, "KICK":self.kick, "PART":self.part, "MODE":self.mode}

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((host, port))
		self.API.sendCommand("NICK {}".format(self.API.getNick()))
		self.API.sendCommand("USER {} 0 * :Bot".format(self.API.getNick()))
		while True:
			motd = self.socket.recv(1024).decode()
			if len(motd) > 0:
				print(motd)
			if "End of message of the day" in motd:
				break

		for channel in self.API.getChannels():
			self.API.sendCommand("JOIN " + channel)

		self.plugins.load()
		self.running = True
		while self.running:
			rlist, wlist, xlist = select([self.socket], [], [], sleepTime)
			if rlist:
				try:
					msg = self.socket.recv(1024).decode()
				except Exception as ex:
					print(ex)
				else:
					for line in msg.split("\r\n"):
						print(line)
						args = line.split(" ")
						if len(args) >= 1 and args[0] in commands:
							commands[args[0]](args)

						elif len(args) >= 2 and args[1] in commands:
							commands[args[1]](args)

						else:
							pass
							
			self.plugins.loop()


	def ping(self, args):
		if len(args) >= 2:
			self.API.sendCommand("PONG " + args[1])

	def privmsg(self, args):
		if len(args) >= 4:
			sender = args[0][1:args[0].find("!")]
			channel = args[2]
			if channel in self.API.getChannels():
				self.plugins.publicMessage(channel, sender, " ".join(args[3:len(args)])[1:])

			elif channel == self.API.getNick():
				self.plugins.privateMessage(channel, sender, " ".join(args[3:len(args)])[1:])


	def join(self, args):
		if len(args) >= 3:
			self.plugins.join(args[2], args[0][1:args[0].find("!")])

	def kick(self, args):
		pass

	def part(self, args):
		pass

	def mode(self, args):
		pass

if __name__ == "__main__":
	Server()
