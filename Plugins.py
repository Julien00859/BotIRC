from importlib import import_module
from os import getcwd
import logging
import os.path


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
                logging.info("Importing " + plugin)
                self.plugins.append(import_module("plugins." + plugin[:plugin.find(".")]))

    def load(self) -> None:
        """Exécute la fonction "on_load(api)" de chaque plugin"""
        for plugin in self.plugins:
            if "on_load" in plugin.__dict__:
                plugin.on_load(self.API)
                logging.info(str(plugin) + " loaded")

    def loop(self) -> None:
        """Exécute la fonction "on_loop()" de chaque plugin """
        for plugin in self.plugins:
            if "on_loop" in plugin.__dict__:
                logging.debug("loop event on " + str(plugin))
                plugin.on_loop()

    def private_message(self, sender: str, message: str) -> None:
        """
        Exécute la fonction "on_private_message(sender, message)" du plugin qui porte le nom donné par le premier
         mot du message
        Exemple ":Julien008!host@indent PRIVMSG MrRobot :essentials stop" enverra un événement au plugin "essentials.py"
        :param sender: le nom de l'utilisateur qui a envoyé le message
        :param message: le message envoyé par l'utilisateur
        """
        for plugin in self.plugins:
            plugin_name = plugin.__name__[plugin.__name__.find(".")+1:].casefold()
            message_plugin = message.split(" ")[0].casefold()
            if plugin_name == message_plugin and "on_private_message" in plugin.__dict__:
                logging.debug("private_message event on " + str(plugin))
                plugin.on_private_message(sender, message)
                break

    def public_message(self, channel: str, sender: str, message: str) -> None:
        """
        Exécute la fonction "on_public_message(channe, sender, message)" de chaque plugin
        :param channel: Le nom du salon sur lequel l'utilisateur a envoyé le message
        :param sender: Le nom de l'utilisateur qui a envoyé le message
        :param message: Le message envoyé par l'utilisateur
        """
        for plugin in self.plugins:
            if "on_public_message" in plugin.__dict__:
                logging.debug("public_message event on " + str(plugin))
                plugin.on_public_message(channel, sender, message)

    def join(self, channel: str, user: str) -> None:
        """
        Exécute la fonction "on_join(channel, user)" de chaque plugin
        :param channel: Le nom du salon que l'utilisateur a rejoint
        :param user: Le nom de l'utilisateur qui a rejoint le salon
        """
        for plugin in self.plugins:
            if "on_join" in plugin.__dict__:
                logging.debug("join event on " + str(plugin))
                plugin.on_join(channel, user)

    def mode(self, sender: str, channel: str, mode: str, user: str) -> None:
        """
        Exécute la fonction "on_mode(channel, mode, user)" de chaque plugin
        :param channel: Le salon concerné par la commande
        :param mode: Le mode que l'utilisateur a perdu ou reçu
        :param user: L'utilisateur pour qui la commande a été appliquée
        """
        for plugin in self.plugins:
            if "on_mode" in plugin.__dict__:
                logging.debug("mode event on " + str(plugin))
                plugin.on_mode(sender, channel, mode, user)

    def quit(self, sender: str) -> None:
        """
        Exécute la fonction "on_kick(sender)" de chaque plugin
        :param sender: Le nom de l'utilisateur qui a quitté le réseau
        """
        for plugin in self.plugins:
            if "on_quit" in plugin.__dict__:
                logging.debug("quit event on " + str(plugin))
                plugin.on_quit(sender)

    def part(self, channel: str, sender: str) -> None:
        """
        Exécute la fonction "on_part(sender, channel)" de chaque plugin
        :param channel: Le nom du salon que l'utilisateur a quitté
        :param sender: Le nom de l'utilisateur qui a quitté le salon
        """
        for plugin in self.plugins:
            if "on_part" in plugin.__dict__:
                logging.debug("part event on " + str(plugin))
                plugin.on_part(channel, sender)

    def kick(self, sender: str, channel: str, user: str) -> None:
        """
        Exécute la fonction "on_kick(sender, channel, user)" de chaque plugin
        :param sender: Le nom de l'utilisateur qui a exécuté la commande /kick
        :param channel: Le nom du salon où l'utilisateur a été kické
        :param user: Le nom de l'utilisateur kické
        """
        for plugin in self.plugins:
            if "on_kick" in plugin.__dict__:
                logging.debug("kick event on " + str(plugin))
                plugin.on_kick(sender, channel, user)

    def stop(self) -> None:
        """
        Exécute la fonction "on_stop()" de chaque plugin
        """
        for plugin in self.plugins:
            if "on_stop" in plugin.__dict__:
                plugin.on_stop()
                logging.info(str(plugin) + " stopped")
