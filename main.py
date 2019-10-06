import datetime
import eel
import json
import logging
import os
import platform
import pypresence
import re
import requests
import subprocess
import threading
import time
import zipfile
import shutil

from pmlauncher import pml, mlogin, mrule

import pycraft
import pycraft.exceptions as pex
from pycraft import authentication

import setup

logger = logging.Logger("MRS")
now = str(datetime.datetime.now())
ndate = now[2:10].replace('-', '')
ntime = now[11:17].replace(':', '')
now = ndate + '_' + ntime
tfm = '%H:%M:%S'
fmt = '[%(levelname)s|%(asctime)s] > %(message)s'
formatter = logging.Formatter(fmt=fmt, datefmt=tfm)
file = logging.FileHandler(f'logs/MRS_{now}.log')
file.setLevel(0)
file.setFormatter(formatter)
stream = logging.StreamHandler()
stream.setLevel(0)
stream.setFormatter(formatter)
logger.addHandler(file)
logger.addHandler(stream)
rpc = pypresence.Presence(490596975457337374)
rpc.connect()

baseDir = os.path.dirname(os.path.realpath(__file__))
launcher = {
    'name': 'MRS Minecraft Launcher',
    'cn': 'ZERO',
    'ver': {
        'major': 0,
        'minor': 0,
        'patch': 0,
        'build': 0,
        'str': "0.0.0.0"
    },
    'path': {
        'main': baseDir,
        'temp': os.path.normpath(baseDir + '/temp'),
        'game': os.path.normpath(baseDir + '/games'),
        'runtime': os.path.normpath(baseDir + '/runtime'),
        'license': os.path.normpath(baseDir + '/LICENSE'),
        'updater': os.path.normpath(baseDir + '/updater.py'),
        'data': os.path.normpath(baseDir + '/data'),
        'mclib': os.path.normpath(baseDir + '/lib'),
        'mcver': os.path.normpath(baseDir + '/versions'),
        'assets': os.path.normpath(baseDir + '/assets')
    },
    'url': {
        'vers': 'https://launchermeta.mojang.com/mc/game/version_manifest.json',
        'list': 'https://api.mysticrs.tk/list',
        'info': 'https://api.mysticrs.tk/modpack',
        'white': 'https://api.mysticrs.tk/whitelist',
        'mpass': 'https://account.mojang.com/password',
        'runtime': 'https://files.mysticrs.tk/{os}/runtime.zip'
    }
}

eel.init('page')


@eel.expose
def close():
    exit()


@eel.expose
def getLauncher():
    global launcher
    return launcher


@eel.expose
def debug(data):
    eel.debug(data)
    return logger.debug(data)


@eel.expose
def info(data):
    eel.info(data)
    return logger.info(data)


@eel.expose
def warn(data):
    eel.warn(data)
    return logger.warn(data)


@eel.expose
def error(data):
    eel.error(data)
    return logger.error(data)


@eel.expose
def fatal(data):
    eel.fatal(data)
    return logger.fatal(data)


try:
    mainThread = threading.Thread(target=eel.start, args=('login.html', 'log.html'), kwargs={'size': (1200, 800)})
    mainThread.start()
except OSError:
    pass


if os.path.exists(os.path.normpath(getLauncher()["path"]["data"] + "/account.mai")):
    eel.loadInfo(json.load(open(os.path.normpath(getLauncher()["path"]["data"] + "/account.mai"))))

session = mlogin.session()  # store game session

@eel.expose
def login(mcid, mcpw):
    try:
        if mcid == "" or mcpw == "":
            warn("Invalid ID or Password!")
        auth_token = pycraft.authentication.AuthenticationToken()
        auth_token.authenticate(mcid, mcpw)

        username = auth_token.profile.name

        global session
        session.access_token = auth_token.access_token
        session.uuid = auth_token.profile.id_
        session.username = username

        info('Logined to ' + username)
        global rpc
        rpc.update(state='Selectting a Modpack', details='Logined to ' + username, large_image='favicon',
                   large_text='Mystic Red Space')
    except pex.YggdrasilError:
        error("Failed to login with " + mcid)
        return False
    return [auth_token.profile.name, auth_token.client_token, auth_token.access_token]


@eel.expose
def isTokenVaild():
    auth_token = pycraft.AuthenticationToken(*(eel.loadToken()()))
    return bool(auth_token.validate())


@eel.expose
def refreshToken():
    auth_token = pycraft.AuthenticationToken(*(eel.loadToken()()))
    auth_token.refresh()

    global session
    session.username = auth_token.profile.name
    session.uuid = auth_token.profile.id_
    session.access_token = auth_token.access_token
    return [auth_token.profile.name, auth_token.client_token, auth_token.access_token]


rpc.update(state='Developing', details='MRS NEW LAUNCHER', large_image='favicon', large_text='Mystic Red Space',
           start=int(time.time()))


def mkd(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def download(path, url):
    dirpath = os.path.dirname(path)
    mkd(dirpath)

    response = requests.get(url, stream=True)
    if int(response.status_code / 100) is not 2:
        return

    with open(path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)


def checkRuntime():
    launcher = getLauncher()
    path = os.path.normpath(launcher["path"]["temp"]+"/runtime.zip")

    if os.path.isfile(path):
        return

    download(path, launcher['url']['runtime'].format(os=mrule.osname))
    with zipfile.ZipFile(path) as f:
        f.extractall(os.path.normpath(launcher["path"]["runtime"]))


def download_event(x):
    info(x.filekind + " - " + x.filename + " - " + str(x.currentvalue) + "/" + str(x.maxvalue))


@eel.expose
def launch(version, name, modpack=False, memory=1):

     ### SESSION
    global session
    session.access_token = "test_token"
    session.uuid = "test_uuid"
    session.username = "hellooooo"

    checkRuntime()

    if mrule.osname == "windows":
        bn = "javaw.exe"
    else:
        bn = "java"
    runtime = os.path.normpath(getLauncher()["path"]["runtime"] + "/bin/" + bn)

    pml.initialize(os.path.normpath(baseDir + '/pml'))
    pml.downloadEventHandler = download_event
    cmd = runtime + " " + pml.startProfile(version, xmx_mb=1024, session=session)

    debug(cmd)
    mc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    rpc.update(state='Playing MRS', details=str(modpack), large_image='favicon', large_text='Mystic Red Space',
               start=int(time.time()))

    while True:
        line = mc.stdout.readline()
        if not line:
            break
        d = line.rstrip()
        print(d)

    if mc.returncode:
        warn(f"Client returned {mc.returncode}!")
    return mc.returncode
