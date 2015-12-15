#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

from importlib import import_module
from os import getcwd
from select import select
import json
import os.path
import socket

class Plugins:
    def __init__(self, api):
        """
        Gestionnaire de plugin
        Importe les plugins python écrits dans /plugins/
        :param api: Un objet API() pour permettre aux plugins de profiter de ses méthodes
        """
        self.API = api

        plugins_path = os.path.join(getcwd(), "plugins")
        if not os.path.exists(plugins_path):
            os.mkdir("plugins")

        self.plugins = []
        for plugin in os.listdir(plugins_path):
            if plugin.endswith(".py") and plugin != "__init__.py":
                self.plugins.append(import_module("plugins." + plugin[:plugin.find(".")]))

    def load(self) -> None:
        for plugin in self.plugins:
            if "onLoad" in plugin.__dict__:
                plugin.onLoad(self.API)

    def loop(self) -> None:
        for plugin in self.plugins:
            if "on_loop" in plugin.__dict__:
                plugin.on_loop(self.API)

    def private_message(self, channel: str, sender: str, message: str) -> None:
        for plugin in self.plugins:
            if "on_private_message" in plugin.__dict__:
                plugin.on_private_message(self.API, channel, sender, message)

    def public_message(self, channel: str, sender: str, message: str) -> None:
        for plugin in self.plugins:
            if "on_public_message" in plugin.__dict__:
                plugin.on_public_message(self.API, channel, sender, message)

    def join(self, channel: str, user: str) -> None:
        for plugin in self.plugins:
            if "on_join" in plugin.__dict__:
                plugin.on_join(self.API, channel, user)

    def stop(self) -> None:
        print("Stopping...")
        for plugin in self.plugins:
            plugin.on_stop()


class API:
    def __init__(self, server: Server):
        self._server = server
        self._config = json.load(open("config.json", "r"))
        self._users = {}

    def stop(self) -> None:
        self._server.plugins.stop()
        self._server.running = False

    def send_command(self, cmd: str) -> None:
        self._server.socket.send("{}\r\n".format(cmd).encode())

    def send_message(self, channel: str, message: str) -> None:
        self.send_command("PRIVMSG {} :{}\r\n".format(channel, message))

    def get_nick(self) -> str:
        return self._config["nickname"]

    def get_channels(self) -> list:
        return self._config["channels"]

class Server:
    def __init__(self):

        self.API = API(self)
        self.plugins = Plugins(self.API)

        with open("config.json", "r") as json_data:
            config = json.load(json_data)
            host = config["host"]
            port = config["port"]
            sleepTime = config["sleepTime"]

        commands = {"PING": self.ping, "PRIVMSG": self.privmsg, "JOIN": self.join, "KICK": self.kick, "PART": self.part,
                    "MODE": self.mode}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.API.send_command("NICK {}".format(self.API.get_nick))
        self.API.send_command("USER {} 0 * :Bot".format(self.API.get_nick))
        while True:
            motd = self.socket.recv(1024).decode()
            if len(motd) > 0:
                print(motd)
            if "End of message of the day" in motd:
                break

        for channel in self.API.get_channels():
            self.API.send_command("JOIN " + channel)

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

    def ping(self, args: list) -> None:
        if len(args) >= 2:
            self.API.send_command("PONG " + args[1])

    def privmsg(self, args: list) -> None:
        if len(args) >= 4:
            sender = args[0][1:args[0].find("!")]
            channel = args[2]
            if channel in self.API.get_channels:
                self.plugins.public_message(channel, sender, " ".join(args[3:len(args)])[1:])

            elif channel == self.API.get_nick:
                self.plugins.private_message(channel, sender, " ".join(args[3:len(args)])[1:])

    def join(self, args: list) -> None:
        if len(args) >= 3:
            self.plugins.join(args[2], args[0][1:args[0].find("!")])

    def kick(self, args: list) -> None:
        pass

    def part(self, args: list) -> None:
        pass

    def mode(self, args: list) -> None:
        pass


if __name__ == "__main__":
    Server()
