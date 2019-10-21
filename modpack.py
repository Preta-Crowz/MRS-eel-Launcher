import os
import json
import requests
from urllib.request import urlretrieve
from event import Event
from event import ProgressEventArgs
import launcher
import util


def getlist():
    return requests.get(launcher.url_list).json()


class ModPackDownloader:
    def __init__(self, root:str, name:str):
        self.name = name
        self.root = root
        self.res = requests.get(url=launcher.url_modpack, params={"name":name}).content.decode("utf8")
        self.event = Event()


    def download(self, localfiles:dict):
        jarr = json.loads(self.res)

        count = len(jarr)
        for i in range(0, count):
            file = jarr[i]
            self.fire(file["name"], i + 1, count)
            
            dirpath = os.path.normpath(self.root + file["dir"])
            filepath = os.path.normpath(dirpath + "/" + file["name"])

            local = localfiles.pop(filepath, None)
            has_file = local != None

            if not has_file or local != file["md5"]:
                if not os.path.isdir(dirpath):
                    os.makedirs(dirpath)
                util.download(file["url"], filepath)


    def fire(self, name, current, allcount):
        self.event.fire(self, ProgressEventArgs(name, current, allcount))
