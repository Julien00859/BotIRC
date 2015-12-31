import Skype4Py
import socket
from select import select
import json

blob = "0c-J8yzfhrgj8L-Iswiv91kDP7N13XBb_Ezn-aDUtQEfqbwj-nJ_DRUo9Y26Mwhb4EHsjDbu-aqklniEV9KLxOU16UwMtaWzhEF8fV68"
skype = Skype4Py.Skype()
skype.Attach()
convo = skype.FindChatUsingBlob(blob)
last_id = convo.Messages[0].Id
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("localhost", 5646))

while True:
    new_msg, wlist, xlist = select([server], [], [], 0.5)
    if new_msg:
        try:
            raw_msg = server.recv(1024).decode()
        except Exception as ex:
            print(ex)
            server.close()
            break
        else:
            if raw_msg:
                json_msg = json.loads(raw_msg)
                sender = json_msg["sender"]
                message = json_msg["message"]
                last_id = convo.SendMessage(sender + ": " + message).Id

    if convo.Messages[0].Id != last_id:
        to_send = convo.Messages[0:map(lambda msg: msg.Id,list(convo.Messages)).index(last_id)]
        for msg in to_send:
            data = {}
            data["sender"] = msg.Sender.DisplayName if msg.Sender.DisplayName else skype.CurrentUser.FullName
            data["message"] = msg.Body
            server.send(json.dumps(data).encode())
        last_id = to_send[0].Id