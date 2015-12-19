import subprocess
import threading

API = None
PROC = None

def read():
    lines = PROC.stdout.readlines().decode()
    if lines:
        print("received from skype")
    for line in lines.split("\n"):
        if len(line) == 0: continue
        print(line)
        API.sendMessage(API.getChannels()[0], line)


def on_public_message(channel, sender, message):
    PROC.stdin.write("sk.write('{}','{}')\n".format(sender, message).encode())
    print("sent to skype")


def on_loop():
    pass


def on_load(api):
    global API
    global PROC
    API = api
    PROC = subprocess.Popen("F:\\Python27\\python.exe plugins\\skype\\wrapper.py", stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def on_stop():
    PROC.kill()
