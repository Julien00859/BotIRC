import json
import logging

class API:
    def __init__(self, server):
        """
        Initialise une API liée à un Server()
        :param server: un objet Server()
        """
        self._server = server
        self._config = json.load(open("config.json", "r"))
        self._channels = {}

    def stop(self, message="Stopped") -> None:
        """
        Arrête proprement le bot.
        :param message: Message à envoyé avec la commande QUIT
        """
        self._server.plugins.stop()  # Donne la main à chaque plugin pour qu'il puisse s'éteindre correctement
        self.send_command("QUIT :" + message)  # Quitte le réseau IRC
        self._server.running = False  # Arrête l'écoute sur le socket

    def send_command(self, cmd: str) -> None:
        """
        Envoie une commande sur le server IRC
        :param cmd: La commande à envoyer
        """
        logging.info(cmd)
        self._server.socket.send("{}\r\n".format(cmd).encode())

    def send_message(self, channel: str, message: str) -> None:
        """
        Envoie un message dans un salon où à un utilisateur
        :param channel: Le nom du salon ou de l'utilisateur où/à qui envoyer le message
        :param message: Le message à envoyer
        """
        self.send_command("PRIVMSG {} :{}\r\n".format(channel, message))

    def send_names_query(self, channel: str) -> None:
        """
        Envoie une requête NAMES et récupère son retour
        :param channel: le nom du salon où envoyer la reqête
        """
        self.send_command("NAMES " + channel)
        names = self._server.socket.recv(1024).decode().splitlines()
        logging.info(names)
        for n in range(len(names)):
            if "End of /NAMES list." in names[n]:
                # :127.0.0.1 353 Julien008 = #Dev :@Julien008 MrRobot
                #                                 [@Julien008,MrRobot]
                for user in " ".join(names[n - 1].split(" ")[5:])[1:].split(" "):
                    self.add_update_user(channel, user)

    def get_bot_nick(self) -> str:
        """
        :return: Le nom du bot sauvegardé dans la configuration
        """
        return self._config["nickname"]

    def get_channels(self) -> list:
        """
        :return: Récupère la liste des salons sauvegardées dans la configuration
        """
        """
        :return:
        """
        return self._config["channels"]

    def add_update_user(self, channel: str, user: str) -> None:
        """
        Ajoute ou met à jour un utilisateur dans le salon donné et calcule son niveau de permission selon
        le prefix de l'utilisateur (@ => OP, % => HALF-OP, + => VOICE)
        :param channel: Le channel où ajouter/update l'utilisateur
        :param user: L'utilisateur
        """
        if user:
            if channel not in self._channels:
                self._channels[channel] = {}

            modes = {"@": ("OP", 4), "%": ("HALF-OF", 3), "+": ("VOICE", 2)}
            if user[:1] in modes:
                if user not in self._channels[channel]:
                    self._channels[channel][user[1:]] = {}
                self._channels[channel][user[1:]]["mode"] = modes[user[:1]]
            else:
                if user not in self._channels[channel]:
                    self._channels[channel][user] = {}
                self._channels[channel][user]["mode"] = ("USER", 1)

    def remove_user(self, channel: str, user: str) -> None:
        """
        Retire un utilisateur d'un channel donné
        :param channel: Le channel que l'utilisateur a quitté
        :param user: L'utilisateur
        """
        if channel in self._channels:
            if user in self._channels[channel]:
                del self._channels[channel][user]
            else:
                err = KeyError("User \"{}\" not found".format(user))
                logging.exception(err)
                raise err
        else:
            err = KeyError("Channel \"{}\" not found".format(channel))
            logging.exception(err)
            raise err

    def get_user_mode(self, user: str, channel: str=None) -> tuple:
        """
        Retourne soit le niveau de permission de l'utilisateur dans le channel spécifié
        soit le plus haut niveau de permission trouvé si aucun salon n'a été spécifié
        :param user: l'utilisateur dont on veut connaître le niveau de permission
        :param channel: (optionnel) le channel où on veut connaitre le niveau de permission
        :return: un tuple dont la première valeur est le nom du mode (OP, HALF-OP, VOICE, USER, DISCONNECTED et la
                 seconde une valeur numérique pour représenter le poids du mode (4: OP .. 0: DISCONNECTED)
        """

        # Si le salon est spécifié, on retourne la permission de l'utilisateur s'il est connecté
        # ou ("DISCONNECTED", 0) s'il n'est pas là
        if channel in self._channels:
            if user in self._channels[channel]:
                return self._channels[channel][user]["mode"]
            else:
                return "DISCONNECTED", 0

        # Sinon retourner le plus haut niveau de permission relatif à l'utilisateur sur tous les salons
        elif channel is None:
            perm = ("DISCONNECTED", 0)
            for channel in self.get_channels():
                mode, lvl = self.get_user_mode(user, channel)
                if perm[1] < lvl:
                    perm = (mode, lvl)
            return perm

        else:
            err = KeyError("Channel \"{}\" not found".format(channel))
            logging.exception(err)
            raise err

    def set_user_mode(self, channel: str, mode: str, user: str) -> tuple:
        """
        Permet de définir le mode de l'utilisateur
        :param channel: Le channel spécifié
        :param mode: Le mode à ajouter
        :param user: L'utilisateur
        """
        modes = {"OP": ("o", 4), "HALF-OP": ("h", 3), "VOICE": ("v", 2), "USER": ("", 1)}
        if channel in self._channels:
            if user in self._channels[channel]:
                if mode in modes:
                    if modes[mode][1] < self._channels[channel][user]["mode"][1]:
                        # Si le nouveau mode est plus bas que l'actuel, on retire l'ancien avant d'appliquer le nouveau
                        self.send_command("MODE {} -{} {}".format(channel,
                                                                  # modes[("OP",4)][0] => "o"
                                                                  modes[self.get_user_mode(user, channel)[0]][0],
                                                                  user)
                                          )

                    self.send_command("MODE {} +{} {}".format(channel, modes[mode][0], user))
                    self._channels[channel][user]["mode"] = (mode, modes[mode][1])
                else:
                    err = ValueError("Invalid mode {} (must be OP, HALF-OP, VOICE or USER)".format(mode))
                    logging.exception(err)
                    raise err
            else:
                err = KeyError("User \"{}\" not found".format(user))
                logging.exception(err)
                raise err
        else:
            err = KeyError("Channel \"{}\" not found".format(channel))
            logging.exception(err)
            raise err

    def get_users(self, channel: str = None):
        """
        Récupère la liste des utilisateurs du réseau (ou en tout cas là où le bot est) ou du salon spécifié
        :param channel: (Optionnel) le salon ciblé par la recherche
        :return: Une liste d'utilisateur
        """
        if channel is None:
            # Retourne la liste de tous les utilisateurs pour chaque salon et supprime les doublons
            return list(set([user for user in self._channels[channel] for channel in self.get_channels()]))

        elif channel in self._channels:
            # Retourne la liste de tous les utilisateurs présents dans un salon
            return [user for user in self._channels[channel]]

        else:
            err = KeyError("Channel \"{}\" not found".format(channel))
            logging.exception(err)
            raise err
