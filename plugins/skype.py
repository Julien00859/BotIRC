import subprocess
import threading

API = None

def read():
    lines = proc.stdout.readline().decode()
    for line in lines.split("\n"):
        if len(line) == 0: continue
        print(line)
        API.sendMessage(API.getChannels()[0], line)


def on_public_message(channel, sender, message):
    proc.stdin.write("sk.write('{}','{}')\r\n".format(sender, message).encode())


def on_loop():
    proc.stdin.write("sk.read()\r\n".encode())


def on_load(api):
    global API
    API = api
    # threading.Thread(target=read, args=(api), daemon=True).start()


def on_stop():
    proc.kill()

proc = subprocess.Popen("F:\\Python27\\python.exe plugins\\skype\\wrapper.py", stdin=subprocess.PIPE)
