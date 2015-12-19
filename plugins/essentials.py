import urllib.request
from bs4 import BeautifulSoup
from sched import scheduler
from threading import Thread
import os.path
from os import getcwd
import random

API = None  # Variable global

"""Fonctions périodiques"""
def period_thread(interval, function):
    # Lance le scheduler dans un nouveau thread
    Thread(target=period_sched, args=(interval, function), daemon=True).start()
def period_sched(interval, function):
    # Schedule la prochaine fonction et après le temps imparti exécute la fonction
    s = scheduler()
    s.enter(interval, 1, period_thread)
    s.run()
    function()


def on_public_message(channel, sender, message):
    if message == "!ping":
        API.send_message(channel, "Pong!")

    elif message == "!quote":
        API.send_message(channel, random.choice(
            open(os.path.join(getcwd(), "plugins", "essentials", "eliot.txt"), "r").readlines()))


def on_private_message(sender, message):
    args = message.split(" ")
    user_perm = API.get_user_permissions(sender)

    if user_perm[0] == "OP":
        if len(args) >= 2 and args[1] == "stop":
            API.stop("We live in a kingdom of bullshit.")

        if len(args) >= 3 and args[1] == "eval":
            eval(" ".join(args[2:]))


def on_stop():
    pass


def on_load(api):
    global API
    API = api
    period_thread(60 * 60 * 24, quote)


def quote():
    soup = BeautifulSoup(urllib.request.urlopen("http://www.softwarequotes.com/").read(), "html.parser")
    qotd = soup.find(id="QuoteoftheDay").getText().replace("\n", "")
    author = soup.find(id="Span1").getText().replace("\n", "")[2:]
    for channel in API.get_channels():
        API.send_command("TOPIC {} {} ~{}".format(channel, qotd, author))
