import socket
import json
from select import select

class Skype():
    def __init__(self, api):
        self.api = api
        self.server = socket.socket()
        self.server.bind(("localhost", 5646))
        self.server.listen(1)

    def loop(self):
        if not "client" in self.__dict__:
            new_one, wlist, xlist = select([self.server], [], [], 0.01)
            if new_one:
                print("[Skype] Connection established")
                self.client, info = self.server.accept()
        else:
            new_msg, wlist, xlist = select([self.client], [], [], 0.01)
            if new_msg:
                try:
                    raw_msg = self.client.recv(1024).decode()
                except:
                    print("[Skype] Connection lost")
                    self.client.close()
                    del self.client
                else:
                    if raw_msg:
                        json_msg = json.loads(raw_msg)
                        sender = json_msg["sender"]
                        message = json_msg["message"]
                        self.api.send_message("#Skype", sender + ": " + message)

    def send_message(self, sender, message):
        if "client" in self.__dict__:
            self.client.send(json.dumps({"sender":sender,"message":message}).encode())

    def stop(self):
        if "client" in self.__dict__:
            self.client.close()
        self.server.close()

def on_load(api):
    global skype
    skype = Skype(api)

def on_public_message(channel, sender, message):
    skype.send_message(sender, message)

def on_loop():
    skype.loop()

def on_stop():
    skype.stop()