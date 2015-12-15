import subprocess
import threading

def read():
	lines = proc.stdout.readline().decode()
	for line in lines.split("\n"):
		if len(line) == 0: continue
		print(line)
		api.sendMessage(api.getChannels()[0], line)

def onPublicMessage(api, channel, sender, message):
	proc.stdin.write("sk.write('{}','{}')\r\n".format(sender, message).encode())

def onLoop(api):
	proc.stdin.write("sk.read()\r\n".encode())

def onLoad(api):
	captureThread = threading.Thread(target=read, args=())
	captureThread.daemon = True
	captureThread.start()

def onStop():
	proc.kill()

proc = subprocess.Popen("F:\\Python27\\python.exe plugins\\skype\\wrapper.py", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
