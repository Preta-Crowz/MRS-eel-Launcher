import requests
import json
from os.path import isfile, isdir, normpath
from os import listdir, remove
import util
import launcher


class WhiteList:
    def __init__(self, root, name):
        jarr = requests.get(url=launcher.url_whitelist, params={'name':name}).json()

        dirs = set()
        files = dict()

        for i in range(0, len(jarr)):
            item = jarr[i]
            path = normpath(item["path"] + item["name"])
            
            if item["dir"]:
                dirs.add(path)
            else:
                files[path] = item["md5"]

        self.dirs = dirs
        self.files = files
        self.root = root


    def getfiles(self):
        return self.getfiles_r(self.root)


    def getfiles_r(self, path):
        files = dict()

        if path in self.dirs:
            return files

        absolute = normpath(path)

        for item in listdir(absolute):
            filepath = normpath(absolute + "/" + item)
            if isfile(filepath):
                fhash = util.md5(filepath)
                files[filepath] = fhash
            else:
                files.update(self.getfiles_r(filepath))

        return files


    def filtering(self, files):
        for key, value in files.items():
            path = normpath(self.root + "/" + key)
            fhash = files.get(path)
            
            if (fhash != None) and (value == None or value == "" or value == fhash):
                files.remove(path)

        for v in files.values():
            remove(v)

