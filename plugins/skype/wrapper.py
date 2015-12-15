import Skype4Py

class Sk():
	def __init__(self):
		self.skype = Skype4Py.Skype()
		self.skype.Attach()
		self.convo = self.skype.FindChatUsingBlob("0_P5lmw2kxmTFLphEgRSeIOWOXbiuagKkZqNzVw2zNyvD2pajWQGTM_7NXFMTHLJsatbzFUSOPk")
		self.historique = self.convo.RecentMessages[-1].Id
		self.offset = 1

	def write(self, sender, message):
		self.convo.SendMessage("%s: %s" % (sender, message))
		self.offset = self.offset + 1

	def read(self):
		if self.convo.RecentMessages[-1].Id != self.historique:
			for msg in self.convo.RecentMessages[map(lambda msg: msg.Id, self.convo.RecentMessages).index(self.historique) + self.offset:len(self.convo.RecentMessages)]:
				print("%s :%s" % (msg.FromDisplayName, msg.Body))
			self.historique = self.convo.RecentMessages[-1].Id
			self.offset = 1

sk = Sk()
while True:
	input()
