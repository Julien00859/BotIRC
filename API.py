import time
import json
import socket

class IRC_API:
	def __init__(self, server, data):
		self.server = server
		self.data = data

	def SendCommand(self, command):
		"""Send a command on the IRC serveur"""
		log(command, "> SERVER")
		self.server.send((command + "\r\n").encode())

	def SendMessage(self, target, message):
		"""Send a message to a target (client/channel) on the IRC serveur"""
		log(target + ": " + message, "> MSG")
		self.server.send(("PRIVMSG " + target + " " + message + "\r\n").encode())

	def GetMessage(self, array, index):
		i = int(0)
		message = str("")
		while i < len(array):
			if i == index:
				if array[i].startswith(":"):
					message = array[i][1:]
				else:
					message = array[i]
			elif i > index:
				message += " " + array[i]
			i+=1
		return message

	def GetSender(self, array):
		"""Get the sender of an IRC message by parsing the command"""
		return array[0][1:array[0].find("!")]

	def GetMode(self, channel, user):
		"""Get the mode of the given user in the given channel"""
		for client in self.data[("clients",channel)]:
			if client[1:] == user or client == user:
				log("Found " + client)

				if client.startswith("@"):
					return (1,"OP","+o")

				elif client.startswith("%"):
					return (2,"HALF-OP","+h")

				elif client.startswith("+"):
					return (3,"VOICE","+v")

				else:
					return (4,"USER", "-v")
		tools.log(user + " not found !", "WARNING")
		return (5, user + " not found !", "-h")

	def GetNameWithoutPrefix(self, user):
		"""Give the name of an user without his prefix"""
		if user.startswith("+") or user.startswith("%") or user.startswith("@"):
			return user[1:]
		else:
			return user	

class Traduction:
	"""Message are stored in json: {"msg":{"Hello":"Salut"}}, we convert it into Python's dict and store into self.lang.
	   For instance, to translate "Hello" all you have to do is:
	   trad = tools.traduction(lang.json)
	   trad.lang["msg"]["Hello"]"""

	def __init__(self, file):
		with open(file, "r") as json_lang:
			self.lang = json.load(json_lang)

class ProgressBar:
    def __init__(self, maxval=100, increment=1):
        self.maxval = maxval
        self.increment = increment
        self.value = 0
        self.maxreached=False
        self.started=time.time()
        print("%3d%% [%20s]" % (0, ""), end="\r")
    def _QBString(self, s, i):
        for n in range(1, int(i)):
            s+=s[0]
        return s
    def step(self):
        if self.maxreached != True:
            self.value+=self.increment
            if self.value==self.maxval:
                self.maxreached=True
                print("%3d%% [%20s] Finished ! (Took %s)" % (self.value/self.maxval*100, self._QBString("=", self.value/self.maxval*20),time.strftime("%Mm %Ss", time.localtime(time.time()-self.started))))
            else:
                print("%3d%% [%20s] Finish in: %s" % (self.value/self.maxval*100,"<" + self._QBString("=", self.value/self.maxval*20),time.strftime("%Mm %Ss", time.localtime((time.time()-self.started)/self.value*(self.maxval-self.value)))),end="\r" )

def log(msg, status="INFO", doIprint=True, doIsave=True):
	"""msg = message to log; file = file where put the message; status = string that will be between []"""
	mytime = time.strftime("%d/%m/%y %H:%M:%S")
	message = mytime + " [" + str(status) + "] " + str(msg)

	if doIprint:
		print(message)

	if doIsave:
		with open("log.txt", "a") as f:
			f.write(message + "\n")
	return message

def ask(question, questionType):
	"""Ask a question to the user, it's answer have to be the same type as the
	   type of (questionType) otherwise we ask him again."""

	#Traduction powa ^^
	trad = Traduction("lang.json")

	if question[-1] != " ": question+= " "

	#Questions and replies are not printed on the screen as the user see well what
	#He is doing with the input(). But Questions and Replies are saved in the log file
	log(question, "QUESTION", False)
	while True:
		answer = input(question)
		log(answer, "REPLY", False)

		#His reply is an str(), if the type of t isn't a str() too, we try to convert
		#his reply in the type wanted, finaly if the reply type is the same type as the t type
		#we return this converted reply. Otherwise... LOOP :D
		if type(questionType) == type(int()):
			try:
				answer = int(answer)
			except:
				pass
		elif type(questionType) == type(bool()):
			try:
				answer = bool(answer)
			except:
				pass

		if type(answer) == type(questionType):
			break
		else:
			log(trad.lang["Tools"]["Ask"]["YouGiveMe"] % (type(r), type(questionType)), "ERROR")
	return answer

def BeautifulJSON(json):
	#Just change {"Plouf":{"Lol":"MDR"}} to:
	#{
	#	"Plouf":{
	#		"Lol":"MDR"
	#	}
	#}
    array = list()
    for l in json:
        array.append(l)
    i = int(0)
    t = int(0)
    for l in array:
        if l == "{":
            l = "{\n"
            t+=1
            for x in range(0, t):
                l += "\t"
        elif l == "}":
            l = "\n"
            t-=1
            for x in range(0, t):
                l += "\t"
            l += "}"
        elif l == "[":
            l = "[\n"
            t+=1
            for x in range(0, t):
                l += "\t"
        elif l == "]":
            l = "\n"
            t-=1
            for x in range(0, t):
                l += "\t"
            l+="]"
        elif l == ",":
            l = ",\n"
            for x in range(0, t):
                l += "\t"
        
        array[i] = l
        i += 1
    json = "".join(array)
    return json