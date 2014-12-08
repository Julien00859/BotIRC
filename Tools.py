import time
import json

class traduction:
	def __init__(self, file):
		with open(file, "r") as json_lang:
			self.lang = json.load(json_lang)

def log(msg, status="INFO", doIprint=True):
	"""msg = message to log; file = file where put the message; status = string that will be between []"""
	mytime = time.strftime("%d/%m/%y %H:%M:%S")
	message = mytime + " [" + str(status) + "] " + str(msg)
	if doIprint == True:
		print(message)
	with open("log.txt", "a") as f:
		f.write(message + "\r\n")
	return message

def ask(q, t):
	trad = traduction("lang/tools.json")
	log(q, "QUESTION", False)
	while True:
		r = input(q)
		log(r, "REPLY", False)
		if type(t) == type(int()):
			try:
				r = int(r)
			except:
				pass

		if type(r) == type(t):
			break
		else:
			log(trad.lang["Ask"]["TypeError"]["YouGiveMe"] + str(type(r)) + trad.lang["Ask"]["TypeError"]["ButINeed"] + str(type(t)), "ERROR")
	return r