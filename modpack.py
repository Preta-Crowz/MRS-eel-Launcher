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
        r = requests.get(url="https://api.mysticrs.tk/modpack", params={"name":name})
        json = json.loads(r)
        
        count = len(json)
        for i in range(0, count):
            file = json[i]
            self.fire(i + 1, count)
            
            dirpath = os.path.normpath(os.path.combine(root, file["dir"]))
            filepath = os.path.normpath(os.path.combine(dirpath, file["name"]))

            local = localfiles.pop(filepath, None)
            has_file = local != None
            
            if not has_file or local != file["md5"]:
                os.makedirs(dirpath)
                urlretreive(file["url"], filepath)


    def fire(self, current, allcount):
        self.event.fire(self, ProgressEventArgs(current, allcount))
