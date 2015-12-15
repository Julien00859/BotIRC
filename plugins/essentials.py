def onPublicMessage(api, channel, sender, message):
	if message == "!stop":
		api.stop()

def onStop():
	pass