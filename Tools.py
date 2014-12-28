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
			f.write(message + "\n")
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
    def SetStatus(self, s):
        self.status=s
    def step(self):
        if self.maxreached != True:
            self.value+=self.increment
            if self.value==self.maxval:
                self.maxreached=True
                print("%3d%% [%20s] Finished ! (Took %s)" % (self.value/self.maxval*100, self._QBString("=", self.value/self.maxval*20),time.strftime("%Mm %Ss", time.localtime(time.time()-self.started))))
            else:
                print("%3d%% [%20s] Finish in: %s" % (self.value/self.maxval*100,"<" + self._QBString("=", self.value/self.maxval*20),time.strftime("%Mm %Ss", time.localtime((time.time()-self.started)/self.value*(self.maxval-self.value)))),end="\r" )
                
def BeautifulJSON(json):
    array = list()
    for l in json:
        array.append(l)
    i = int(0)
    t = int(0)
    for l in array:
        if l == "{":
            l = "{\r\n"
            t+=1
            for x in range(0, t):
                l += "\t"
        elif l == "}":
            l = "\r\n"
            t-=1
            for x in range(0, t):
                l += "\t"
            l += "}"
        elif l == "[":
            l = "[\r\n"
            t+=1
            for x in range(0, t):
                l += "\t"
        elif l == "]":
            l = "\r\n"
            t-=1
            for x in range(0, t):
                l += "\t"
            l+="]"
        elif l == ",":
            l = ",\r\n"
            for x in range(0, t):
                l += "\t"
        
        array[i] = l
        i += 1
    json = "".join(array)
    return json