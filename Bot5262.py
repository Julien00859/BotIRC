import socket
import sys
import threading
import pickle
import hashlib
import requests
from bs4 import BeautifulSoup
import requests
import time

server="192.168.1.32"
port=6667
botname="Bot5262"
chan="#DevBukkit"
password="macaroni"

try:
    with open("id","rb") as file:
        MonPick = pickle.Unpickler(file)
        id = MonPick.load()
except FileNotFoundError:
    id={}

def sendmsg(user, msg):
    irc.send(("PRIVMSG " + user + " " + msg + "\r\n").encode("UTF-8"))
    print(user +" " + botname + ":" + msg)

def fcommand(linex, i):
    command = str()
    for x in range(i, len(linex)):
        command+=linex[x] + " "
    return command

def fsender(chaine):
    sender = str()
    b = True
    for lettre in chaine:
        if lettre != ":" and b == True and lettre != "!":
            sender+=lettre
        if lettre == "!":
            b = False
    return sender

class ShoutBox(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)        
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

    def run(self):
        uuid=int(0)
        b = False
        while self.stopped() == False:
            main = requests.get("http://devbukkit.fr/forum/data/taigachat/messages.html")
            text = main.text.replace("\\", "")
            if main.status_code == 200:
                soup = BeautifulSoup(text)
                for poste in soup.findAll("li"):
                    if len(poste)>3:
                        for i in range(1,75):
                            if int(poste.get("data-messageid")) > uuid:
                                uuid = int(poste.get("data-messageid"))
                                for useful in poste:
                                    if len(useful)>2 and useful.get('class')!=["Popup"]:
                                        message = useful.get_text()
                                        if b:
                                            message = message.replace("u00e0", "à")
                                            message = message.replace("u00e9", "é")
                                            message = message.replace("u00e8", "è")
                                            message = message.replace("u00ea", "ê")
                                            message = message.replace("u00ee", "î")
                                            message = message.replace("u00f4", "ô")
                                            message = message.replace("u00f9", "ù")
                                            sendmsg(chan, message)

            else:
                print("Warning ! " + str(main.status_code))
            b=True
            time.sleep(3)

class Bot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

    def run(self):
        isConnected = False
        readbuffer = ""
        
        while self.stopped() == False:
            readbuffer += irc.recv(1024).decode("UTF-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            for line in temp:
                linex = line.rstrip()
                linex = linex.split()
                
                if linex[0] == "PING":
                    irc.send(("PONG " + linex[1] + "\r\n").encode("UTF-8"))
                    if isConnected == False:
                        isConnected = True
                        irc.send(("JOIN " + chan + "\r\n").encode("UTF-8"))
                        print("Pong ! %s joined %s and is ready to receive commands !\n" % (botname, chan) )
                        


                elif linex[1] == "MODE" and linex[2] == chan:
                    id[linex[4],"mode"] = linex[3]
                    with open("id","wb") as file:
                        mp = pickle.Pickler(file)
                        mp.dump(id)
                
                elif len(linex) > 3 and linex[1] == "PRIVMSG":
                    sender = fsender(linex[0])
                    if linex[2] == chan:
                        print(linex[2] + " " + sender + fcommand(linex, 3))

                        if linex[3].lower() == ":.ping":
                            sendmsg(chan, "Pong ! " + fcommand(linex, 4))
                        
                        elif linex[3].lower() == ":.help":
                            sendmsg(chan, "=== HELP ===")
                            sendmsg(chan, ".ping - Ping the bot")
                            sendmsg(chan, ".help - Show this help page")
                            sendmsg(chan, "/MSG " + botname + " identify <password> - Authentication to get your rank")
                            sendmsg(chan, "/MSG " + botname + " changepwd <oldPassword> <newPassword> - Change your password")
                    
                    if linex[2] == botname:
                        if linex[3].lower() == ":identify" and len(linex)>4:
                        
                            try:
                                if id[sender,"password"] == hashlib.sha1((linex[4]).encode()).hexdigest():
                                    irc.send(("MODE %s %s %s \c\n" % (chan, id[sender,"mode"], sender)).encode())
                                    sendmsg(chan, sender + " is now logged")
                                else:
                                    sendmsg(sender, "Wrong password !")
                                    
                            except KeyError:
                                id[sender,"password"] = hashlib.sha1((linex[4]).encode()).hexdigest()
                                try:
                                    id[sender,"mode"]
                                except KeyError:
                                    sendmsg(sender, "You don't have any group set.")
                                    id[sender,"mode"] = ""
                                print(sender + " is now registered")
                                sendmsg(chan, sender + " is now registered")
                                with open("id","wb") as file:
                                    mp = pickle.Pickler(file)
                                    mp.dump(id)
                        elif linex[3].lower() == ":changepwd" and len(linex)>5:
                            if id[sender,"password"] == hashlib.sha1((linex[4]).encode()).hexdigest():
                                id[sender,"password"] = hashlib.sha1((linex[5]).encode()).hexdigest()
                                sendmsg(sender, "Password changed !")
                                with open("id","wb") as file:
                                    mp = pickle.Pickler(file)
                                    mp.dump(id)
                            else:
                                sendmsg(sender, "Wrong password !")
                                
                        elif linex[3] == ":" + password:
                            print(linex)
                            
                            if linex[4].lower() == "tell":
                                sendmsg(chan, fcommand(linex, 5))                            
                            elif linex[4].lower() == "op":
                                irc.send(("MODE %s +o %s \n" % (chan, sender)).encode("UTF-8"))                                
                            elif linex[4].lower() == "sudo":
                                    irc.send((fcommand(linex, 5) + "\n").encode("UTF-8"))
                            elif linex[4].lower() == "stop":
                                    irc.send(("QUIT Have to go ! My planet needs me !\n").encode("UTF-8"))
                                    print("\nStopped ! Press any key to quit.")
                                    self._stop.set()
                        else:
                            print(linex[2] + " " + sender + fcommand(linex, 3))

irc = socket.socket()
print("Establishing connection to %s:%i" % (server, port))
irc.connect((server, port))

irc.recv(1024).decode()
print("Connection established !")

print("Connecting %s..." % botname)
irc.send(("USER %s %s %s: Bot \r\n" % (botname, botname, botname)).encode("UTF-8"))
irc.send(("NICK " + botname + "\r\n").encode("UTF-8"))
print("Connected ! Waiting server ping to join " + chan + "...")

MonBot = Bot()
MonBot.start()
MaShout = ShoutBox()
MaShout.start()

while MonBot.stopped() == False:
    msg = input()
    if msg.startswith("/") and MonBot.isAlive():
        msg = msg[msg.find("/")+1:].split(" ")
        if msg[0].lower() == "op" and len(msg)>1:
            irc.send(("MODE %s +o %s\n" % (chan, msg[1])).encode("UTF-8"))
        elif msg[0].lower() == "join" and len(msg)>1:
            irc.send(("CLOSE \n\r").encode("UTF-8"))
            chan = msg[1]
            msg = " ".join(msg)
            irc.send((msg[msg.find("/") + 1:] + "\n\r").encode("UTF-8"))
        elif msg[0].lower() == "stop":
            MonBot.stop()
        else:
            msg = " ".join(msg)
            irc.send((msg[msg.find("/") + 1:] + "\n\r").encode("UTF-8"))
    elif MonBot.stopped() == False:
        sendmsg(chan, msg)

MaShout.stop()