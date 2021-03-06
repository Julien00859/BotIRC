#!/usr/local/bin/python3.5

from select import select
from sys import stderr
import json
import logging
import socket
from API import API
from Plugins import Plugins


class Server:
    def __init__(self):
        # Chargement de la configuration
        with open("config.json", "r") as json_data:
            config = json.load(json_data)
            host = config["host"]
            port = config["port"]
            sleep_time = config["sleepTime"]
            nick = config["nickname"]
            oper_password = config["oper_password"]
            log_file = config["log_file"]
            log_level = config["log_level"]

        logging.basicConfig(filename=log_file,
                            filemode="a",
                            level=getattr(logging, log_level.upper()),
                            format='%(asctime)s [%(levelname)s | %(filename)s > %(funcName)s] %(message)s',
                            datefmt='%x %X')
        stderr = open(log_file, "a")

        logging.info("=== Starting bot ===")
        logging.info("Loading API")
        self.API = API(self)
        logging.info("Loading plugins")
        self.plugins = Plugins(self.API)

        logging.info("Connecting to the IRC network")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.API.send_command("NICK {}".format(nick))
        self.API.send_command("USER {} 0 * :Bot".format(nick))
        while True:
            motd = self.socket.recv(1024).decode()
            if len(motd) > 0:
                for line in motd.splitlines():
                    logging.info(line)
            if "Current Global Users" in motd:
                break

        self.API.send_command("OPER Bot {}".format(oper_password))
        for line in self.socket.recv(1024).decode().splitlines():
            logging.info(line)

        for channel in self.API.get_channels():
            self.API.send_command("JOIN " + channel)
            for line in self.socket.recv(1024).decode().splitlines():
                logging.info(line)
            self.API.send_command("SAMode {} +o {}".format(channel, nick))
            for line in self.socket.recv(1024).decode().splitlines():
                logging.info(line)
            self.API.send_names_query(channel)

        logging.info("Connected !")
        logging.info("Loading plugins")

        self.plugins.load()

        commands = {
            "PING": self.ping,
            "PRIVMSG": self.privmsg,
            "JOIN": self.join,
            "KICK": self.kick,
            "PART": self.part,
            "MODE": self.mode,
            "QUIT": self.quit
        }

        logging.info("Starting main-loop")
        self.API.send_command("PONG :127.0.0.1")
        self.running = True
        while self.running:
            rlist, wlist, xlist = select([self.socket], [], [], sleep_time)
            if rlist:
                try:
                    msg = self.socket.recv(1024).decode()
                except Exception as ex:
                    logging.exception(ex)
                else:
                    for line in msg.splitlines():
                        logging.info(line)
                        args = line.split(" ")
                        if len(args) >= 1 and args[0] in commands:
                            commands[args[0]](args)

                        elif len(args) >= 2 and args[1] in commands:
                            commands[args[1]](args)

                        else:
                            pass

            self.plugins.loop()

        self.socket.close()

    def ping(self, args: list) -> None:
        # PING :127.0.0.1
        if len(args) >= 2:
            self.API.send_command("PONG " + args[1])

    def privmsg(self, args: list) -> None:
        if len(args) >= 4:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be PRIVMSG #Dev :plop
            #  ^^^^^^^^^^^                                                  ^^^^
            sender = args[0][1:args[0].find("!")]  # Julien00859
            channel = args[2]  # #Dev
            if channel in self.API.get_channels():
                self.plugins.public_message(channel, sender, " ".join(args[3:len(args)])[1:])

            elif channel == self.API.get_bot_nick():
                self.plugins.private_message(sender, " ".join(args[3:len(args)])[1:])

    def join(self, args: list) -> None:
        if len(args) >= 3:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be JOIN :#Dev
            #  ^^^^^^^^^^^                                                ^^^^
            sender = args[0][1:args[0].find("!")]  # Julien00859
            channel = args[2][1:]  # #Dev
            self.API.add_update_user(channel, sender)
            self.plugins.join(channel, sender)

    def kick(self, args: list) -> None:
        # :Julien008!Julien@host-85-201-171-39.dynamic.voo.be KICK #Dev Julien00859 :You have been kicked
        #  ^^^^^^^^^                                               ^^^^ ^^^^^^^^^^^
        if len(args) >= 4:
            sender = args[0][1:args[0].find("!")]  # Julien008
            self.API.remove_user(args[2], args[3])
            self.plugins.kick(sender, args[2], args[3])

    def part(self, args: list) -> None:
        if len(args) >= 3:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be PART #Dev :"Gonna bake some cookies..."
            #  ^^^^^^^^^^^                                               ^^^^
            sender = args[0][1:args[0].find("!")]  # Julien00859
            self.API.remove_user(args[2], sender)
            self.plugins.part(args[2], sender)

    def mode(self, args: list) -> None:
        # :Julien008!Julien@host-85-201-171-39.dynamic.voo.be MODE #Dev +h Julien00859
        #  ^^^^^^^^^                                               ^^^^ ^^ ^^^^^^^^^^^

        sender = args[0][1:args[0].find("!")]  # Julien008
        if len(args) >= 5:
            self.API.send_names_query(args[2])
            self.plugins.mode(sender, args[2], args[3], args[4])

    def quit(self, args: list) -> None:
        if len(args) >= 1:
            # :Julien00859!Julien@host-85-201-171-39.dynamic.voo.be QUIT :Quit: Keep calm and do not rage quit
            #  ^^^^^^^^^^^
            sender = args[0][1:args[0].find("!")]  # Julien00859
            for channel in self.API.get_channels():
                self.API.remove_user(channel, sender)
                self.plugins.quit(sender)

if __name__ == "__main__":
    Server()
