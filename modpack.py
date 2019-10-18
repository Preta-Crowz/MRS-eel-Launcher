import os
import json
import requests
from urllib.request import urlretrieve
from event import Event
from event import ProgressEventArgs


def getlist():
    r = requests.get("https://api.mysticrs.tk/list")
    return json.loads(r)


class ModPackDownloader:
    def __init__(self):
        self.event = event()


    def download(self, root, localfiles):
        pass


    def fire(self, current, allcount):
        self.event.fire(self, ProgressEventArgs(current, allcount))
