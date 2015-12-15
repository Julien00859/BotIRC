def on_public_message(api, channel, sender, message):
    if message == "!stop":
        api.stop()
    elif message == "!ping":
        api.send_message(channel, "Pong!")

def on_stop():
    pass
