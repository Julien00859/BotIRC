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
            if "on_load" in plugin.__dict__:
                plugin.on_load(self.API)

    def loop(self) -> None:
        for plugin in self.plugins:
            if "on_loop" in plugin.__dict__:
                plugin.on_loop()

    def private_message(self, sender: str, message: str) -> None:
        for plugin in self.plugins:
            plugin_name = plugin.__name__[plugin.__name__.find(".")+1:].casefold()
            message_plugin = message.split(" ")[0].casefold()
            if plugin_name == message_plugin and "on_private_message" in plugin.__dict__:
                plugin.on_private_message(sender, message)
                break

    def public_message(self, channel: str, sender: str, message: str) -> None:
        for plugin in self.plugins:
            if "on_public_message" in plugin.__dict__:
                plugin.on_public_message(channel, sender, message)

    def join(self, channel: str, user: str) -> None:
        for plugin in self.plugins:
            if "on_join" in plugin.__dict__:
                plugin.on_join(channel, user)

    def stop(self) -> None:
        print("Stopping...")
        for plugin in self.plugins:
            plugin.on_stop()


class API:
    def __init__(self, server):
        self._server = server
        self._config = json.load(open("config.json", "r"))
        self._channels = {}

    def stop(self, message="Stopped") -> None:
        self._server.plugins.stop()
        self.send_command("QUIT :" + message)
        self._server.running = False

    def send_command(self, cmd: str) -> None:
        self._server.socket.send("{}\r\n".format(cmd).encode())

    def send_message(self, channel: str, message: str) -> None:
        self.send_command("PRIVMSG {} :{}\r\n".format(channel, message))

    def get_bot_nick(self) -> str:
        return self._config["nickname"]

    def get_channels(self) -> list:
        return self._config["channels"]

    def add_update_user(self, channel: str, user: str) -> None:
        if user:
            if channel not in self._channels:
                self._channels[channel] = {}

            modes = {"@":("OP", 4), "%":("HALF-OF", 3), "+":("VOICE", 2)}
            if user[:1] in modes:
                if user not in self._channels[channel]:
                    self._channels[channel][user[1:]] = {}
                self._channels[channel][user[1:]]["permission"] = modes[user[:1]]
            else:
                if user not in self._channels[channel]:
                    self._channels[channel][user] = {}
                self._channels[channel][user]["permission"] = ("USER",1)

    def remove_user(self, channel: str, user: str) -> None:
        if channel in self._channels:
            if user in self._channels[channel]:
                del self._channels[channel][user]
            else:
                raise ValueError("User \"{}\" not found".format(user))
        else:
            raise ValueError("Channel \"{}\" not found".format(channel))

    def get_user_permissions(self, user: str, channel: str=None) -> tuple:
        # Si un channel est spécifié, retourner le niveau de permission relatif à ce salon
        if channel in self._channels:
            if user in self._channels[channel]:
                return self._channels[channel][user]["permission"]
            else:
                return "DISCONNECTED", 0

        # Sinon retourner le plus haut niveau de permission relatif à l'utilisateur sur tous les salons
        elif channel is None:
            perm = ("USER",0)
            for channel in self.get_channels():
                mode, lvl = self.get_user_permissions(user, channel)
                if perm[1] < lvl:
                    perm = (mode, lvl)
            return perm

        else:
            raise ValueError("Channel \"{}\" not found".format(channel))


class Server:
    def __init__(self):

        self.API = API(self)
        self.plugins = Plugins(self.API)

        with open("config.json", "r") as json_data:
            config = json.load(json_data)
            host = config["host"]
            port = config["port"]
            sleep_time = config["sleepTime"]
            nick = config["nickname"]
            oper_password = config["oper_password"]

        commands = {"PING": self.ping, "PRIVMSG": self.privmsg, "JOIN": self.join, "KICK": self.kick, "PART": self.part, "MODE": self.mode, "QUIT": self.quit}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.API.send_command("NICK {}".format(nick))
        self.API.send_command("USER {} 0 * :Bot".format(nick))
        while True:
            motd = self.socket.recv(1024).decode()
            if len(motd) > 0:
                print(motd)
            if "Current Global Users" in motd:
                break

        self.API.send_command("OPER Bot {}".format(oper_password))
        print(self.socket.recv(1024).decode())

        for channel in self.API.get_channels():
            self.API.send_command("JOIN " + channel)

            #Prend la main pour lire le /NAMES lié au /join
            names = self.socket.recv(1024).decode().split("\r\n")
            for n in range(len(names)):
                if "End of /NAMES list." in names[n]:
                    # :127.0.0.1 353 Julien008 = #Dev :@Julien008 MrRobot
                    #                                 [@Julien008,MrRobot]
                    for user in " ".join(names[n-1].split(" ")[5:])[1:].split(" "):
                        self.API.add_update_user(channel, user)

            self.API.send_command("SAMode {} +o {}".format(channel, nick))

        self.plugins.load()
        self.running = True
        while self.running:
            rlist, wlist, xlist = select([self.socket], [], [], sleep_time)
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
        # PING :127.0.0.1
        if len(args) >= 2:
            self.API.send_command("PONG " + args[1])

    def privmsg(self, args: list) -> None:
        if len(args) >= 4:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be PRIVMSG #Dev :plop
            #  ^^^^^^^^^^^                                                  ^^^^
            sender = args[0][1:args[0].find("!")] # Julien00859
            channel = args[2] # #Dev
            if channel in self.API.get_channels():
                self.plugins.public_message(channel, sender, " ".join(args[3:len(args)])[1:])

            elif channel == self.API.get_bot_nick():
                self.plugins.private_message(sender, " ".join(args[3:len(args)])[1:])

    def join(self, args: list) -> None:
        if len(args) >= 3:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be JOIN :#Dev
            #  ^^^^^^^^^^^                                                ^^^^
            sender = args[0][1:args[0].find("!")] # Julien00859
            channel = args[2][1:] # #Dev
            self.plugins.join(channel, sender)
            self.API.add_update_user(channel, sender)

    def kick(self, args: list) -> None:
        # :Julien008!Julien@host-85-201-171-39.dynamic.voo.be KICK #Dev Julien00859 :Julien008
        #                                                          ^^^^ ^^^^^^^^^^^
        if len(args) >= 4:
            self.API.remove_user(args[2], args[3])

    def part(self, args: list) -> None:
        if len(args) >= 3:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be PART #Dev :"Gonna bake some cookies..."
            #  ^^^^^^^^^^^                                               ^^^^
            sender = args[0][1:args[0].find("!")] # Julien00859
            self.API.remove_user(args[2], sender)

    def mode(self, args: list) -> None:
        # :Julien008!Julien@host-85-201-171-39.dynamic.voo.be MODE #Dev +h Julien00859
        #                                                          ^^^^    ^^^^^^^^^^^

        # Reprend la main sur le socket pour envoyer un /NAMES sur le channel concerné par la commande et analyser son retour
        if len(args) >= 5:
            channel = args[2]
            user = args[4]
            self.API.send_command("NAMES " + channel)
            names = self.socket.recv(1024).decode().split("\r\n")
            for n in range(len(names)):
                if "End of /NAMES list." in names[n]:
                    # :127.0.0.1 353 Julien008 = #Dev :@Julien008 MrRobot
                    #                                 [@Julien008,MrRobot]
                    for user in " ".join(names[n-1].split(" ")[5:])[1:].split(" "):
                        self.API.add_update_user(channel, user)

    def quit(self, args: list) -> None:
        if len(args) >= 1:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be QUIT :Quit: Keep calm and do not rage quit
            #  ^^^^^^^^^^^
            sender = args[0][1:args[0].find("!")] # Julien00859
            for channel in self.API.get_channels():
                self.API.remove_user(channel, sender)


if __name__ == "__main__":
    Server()
