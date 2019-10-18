import requests
import json
from os.path import combine, isfile
from os import listdir
import util


class whitelist:
    def __init__(self, root, name):
        r = requests.get(url="https://api.mysticrs.tk/whitelist", params={'name'}:name)
        json = json.loads(r)

        dirs = set()
        files = dict()

        for item in json:
            path = combine(item["path"], item["name"])
            
            if item["dir"]:
                dirs.append(path)
            else:
                files.append(path, item["md5"])

        self.dirs = dirs
        self.files = files
        self.root = root


    def getfiles(self, path):
        files = dict()

        if path in dirs:
            return files

        absolute = combine(self.root, path)

        for item in listdir(absolute):
            filepath = combine(absolute, item)
            if isfile(filepath):
                files.append(filepath, util.md5(filepath))
            else:
                files.extend(getfiles(self, filepath))

        return files


    def filtering(self, files):
        for key, value in files.items():
            path = combine(self.root, key)
            fhash = files.get(path)
            
            if (fhash != None) and (value == None or value == "" or value == fhash):
                files.remove(path)

        for v in files.values():
            os.remove(v)

