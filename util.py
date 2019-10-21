import hashlib
import os
import requests
import shutil
import urllib3
from pmlauncher import mrule
import codecs


def md5(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download(url, path):
    dirpath = os.path.dirname(path)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)

    response = requests.get(url, stream=True, verify=False)
    if int(response.status_code / 100) is not 2:
        return  # TODO : Raise Exception

    with open(path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)
        

def osType():
    return mrule.osname


def readfile(path):
    f = codecs.open(path, 'r', encoding='utf8')
    content = f.read()
    f.close()
    return content


def writefile(path, content):
    dpath = os.path.dirname(path)
    if not os.path.isdir(dpath):
        os.makedirs(dpath)

    f = codecs.open(path, 'w', encoding='utf8')
    f.write(content)
    f.close()

