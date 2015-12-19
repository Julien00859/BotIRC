import urllib.request
from bs4 import BeautifulSoup
import re

url_regex = re.compile("(http(s)?://)?([A-Za-z0-9\-_%]{1,}\.)?[A-Za-z0-9\-_%]{1,}\.(aero|biz|com|coop|edu|info|int|net|org|mil|museum|name|pro|gov|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cx|cy|cz|de|dk|dj|dm|do|dz|ec|ee|eg|eh|er|es|et|fi|fj|fk|fm|fo|fr|fx|ga|gd|ge|gf|gg|gh|gi|gl|gn|gp|gq|gr|gs|gt|gu|gy|hk|hm|hn|hr|ht|hu|id|ie|il|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mx|mw|my|mz|na|nc|nf|ne|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|ph|pk|pl|pm|pn|pq|pr|pt|py|pw|qa|re|ro|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|sv|sy|sz|tc|td|tf|th|tj|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zr|zm|zw)([A-Za-z0-9\-/_%\.]{0,})?")
ip_regex = re.compile("(http(s)?://)?([0-9]{1,3}\.){3}[0-9]{1,3}(/[A-Za-z0-9\-/_%\.]{0,})?")

API = None  # Variable global


def on_load(api):
    global API
    API = api


def on_stop():
    pass


def on_public_message(channel, sender, message):
    match = url_regex.search(message)
    if match:
        arg = match.group(0) if match.group(0).startswith("http") else "http://" + match.group(0)
        try:
            API.send_message(channel, "{} [{}]".format(BeautifulSoup(urllib.request.urlopen(arg).read(), "html.parser").title.getText().replace("\n", ""), arg))
        except:
            pass
    else:
        match = ip_regex.search(message)
        if match:
            arg = match.group(0) if match.group(0).startswith("http") else "http://" + match.group(0)
            try:
                API.send_message(channel, "{} [{}]".format(BeautifulSoup(urllib.request.urlopen(arg).read(), "html.parser").title.getText().replace("\n", ""), arg))
            except:
                pass
