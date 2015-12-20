import json
from os import getcwd, listdir
from os.path import join
from hashlib import sha256

API = None
auth = None

def on_load(api):
    global API
    global auth
    API = api

    if "auth.json" in listdir(join(getcwd(), "plugins")):
        auth = json.load(open(join(getcwd(), "plugins", "auth.json")), "r")
    else:
        auth = {}

    # On récupère les modes de chaque utilisateur dans chaque channel
    # on sauvegarde ce mode si l'utilisateur n'est pas gélé (déjà enregistré)
    for channel in API.get_channels():
        for user in API.get_users(channel):
            if user not in auth or "password" not in auth[user]:
                auth[user] = {}
                auth[user]["authenticated"] = False
                auth[user]["channels"] = {}
                auth[user]["channels"][channel] = API.get_user_mode(user, channel)[0]
            else:
                # Utilisateur gelé, on ne le modifie pas
                pass


def on_stop():
    json.dump(auth, open(join(getcwd(), "plugins", "auth.json"), "w"), indent="\t", sort_keys=True)


def on_private_message(sender, message):
    args = message.split(" ")
    if len(args) >= 2:
        if args[1].casefold() == "login":
            # auth login password

            if len(args) >= 3:
                if sender in auth and "password" in auth[sender]:
                    if sha256(args[2].encode()).hexdigest() == auth[sender]["password"]:
                        # L'authentification est réussie
                        # Maintenant on envoie un /MODE dans tous les salons où il se trouve
                        auth[sender]["authenticated"] = True
                        for channel in API.get_channels:
                            if sender in API.get_users(channel) and channel in auth[sender]["channels"]:
                                API.set_user_mode(channel, auth[sender][channel], sender)
                        API.send_message(sender, "[AUTH] Authentication successful.")
                    else:
                        API.send_message(sender, "[AUTH] Invalid password !")
                else:
                    API.send_message(sender, "[AUTH] You are not registered yet ! Please type: \"/msg {} auth register {}\" to register your account".format(API.get_bot_nick(), args[2]))
            else:
                API.send_message(sender, "[AUTH] Usage: \"/msg {} login your_password\"".format(API.get_bot_nick()))

        elif args[1].casefold() == "register":
            # auth register password

            if len(args) >= 3:
                if sender not in auth:
                    auth[sender] = {}

                if "password" not in auth[sender]:
                    auth[sender]["password"] = sha256(args[2].encode()).hexdigest()
                    auth[sender]["authenticated"] = True
                    API.send_message(sender, "[AUTH] You have been registered.")
                else:
                    API.send_message(sender, "[AUTH] You are already registered ! Please type: \"/msg {} auth login {}\" to login with your account".format(API.get_bot_nick(), args[2]))
            else:
                API.send_message(sender, "[AUTH] Usage: \"/msg {} register a_password\"".format(API.get_bot_nick()))

        elif args[1].casefold() == "setmode":
            # auth setmode channel mode user
            pass

        elif args[1].casefold() == "isauthenticated":
            pass

        elif args[1].casefold() == "help":
            pass

        else:
            pass

    else:
        API.send_message(sender, "[AUTH] Type \"/msg {} auth help\" to show the help page".format(API.get_bot_nick()))


def on_join(channel, user):
    print("on_join event !")
    if user not in auth or "password" not in auth[user]:
        # L'utilisateur est absent de la mapping ou ne s'est pas encore enregistré
        auth[user] = {}
        auth[user]["channels"][channel] = API.get_user_permissions(user, channel)[0]
        auth[user]["authenticated"] = False
        API.send_message(user, "[AUTH] The channel {} is protected by authentication, to register your nickname, type \"/msg {} auth register a_password_here\"".format(channel, API.get_bot_nick()))

    elif auth[user]["authenticated"]:
        # L'utilisateur est enregistré et authentifié
        API.set_user_mode(channel, auth[user]["channels"][channel], user)

    else:
        # L'utilisateur n'est pas encore authentifié
        API.send_message(user, "[AUTH] The channel {} require you to authenticate ! Type \"/msg {} auth login your_password_here\" ".format(channel, API.get_bot_nick()))


def on_mode(sender, channel, mode, user):
    if user not in auth or "password" not in auth[user]:
        # Permet de mettre le mode de l'utilisateur dynamiquement à jour avant son enregistrement
        auth[user] = {}
        auth[user]["authenticated"] = False
        auth[user]["channels"] = {}
        auth[user]["channels"][channel] = API.get_user_mode(user, channel)[0]

    elif sender != API.get_bot_nick():
        # Si l'utilisateur est déjà enregistré, alors son mode est gelé
        # On rappelle la commande pour mettre à jour le mode d'un utilisateur déjà enregistré

        modes = {"+o": "OP", "+h": "HALF-OP", "+v": "VOICE"}
        if mode in modes:
            mode = modes[mode]
        else:
            mode = "USER"

        for user in API.get_users(channel):
            if API.get_user_mode(user, channel)[0] == "OP":
                API.send_message(user, "[AUTH] User mode is frozen for {0}, to change its internal mode please type: \"/msg {1} auth setmode {2} {3} {0}\"".format(user, API.get_bot_nick(), channel, mode))
