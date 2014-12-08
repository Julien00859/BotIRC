import time
import json

class traduction:
	def __init__(self, file):
		with open(file, "r") as json_lang:
			self.lang = json.load(json_lang)

def log(msg, status="INFO", doIprint=True, doIsave=True):
	"""msg = message to log; file = file where put the message; status = string that will be between []"""
	mytime = time.strftime("%d/%m/%y %H:%M:%S")
	message = mytime + " [" + str(status) + "] " + str(msg)
	if doIprint:
		print(message)

	if doIsave:
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
			log(trad.lang["Ask"]["TypeError"]["YouGiveMe"] % (type(r), type(t)), "ERROR")
	return r