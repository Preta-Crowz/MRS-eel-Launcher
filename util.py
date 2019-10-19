import hashlib
import os
import requests
import shutil
from pmlauncher import mrule


def md5(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def download(url, path):
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath)

    response = requests.get(url, stream=True, verify=False)
    if int(response.status_code / 100) is not 2:
        return  # TODO : Raise Exception

    with open(path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)
        

def osType():
    return mrule.osname
