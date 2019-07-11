import json, os, pypresence, logging, time, threading, eel
import pycraft
from pycraft import authentication
import pycraft.exceptions as pex
logger = logging.Logger("MRS")
rpc = pypresence.Presence(490596975457337374)
rpc.connect()

baseDir = os.path.dirname(os.path.realpath(__file__))+'/'
launcher = {
  'name':'MRS Minecraft Launcher',
  'cn':'CODENAME_ZERO',
  'ver':{
    'major':0,
    'minor':0,
    'patch':0,
    'build':0
  },
  'path':{
    'main':baseDir,
    'game':os.path.normpath(baseDir+'./games/'),
    'java':os.path.normpath(baseDir+'./runtime/'),
    'license':os.path.normpath(baseDir+'./LICENSE'),
    'updater':os.path.normpath(baseDir+'./updater.py'),
    'data':os.path.normpath(baseDir+'./data/'),
    'mclib':os.path.normpath(baseDir+'./forge/'),
  },
  'url':{
    'list':'https://api.mysticrs.tk/list',
    'info':'https://api.mysticrs.tk/modpack',
    'white':'https://api.mysticrs.tk/whitelist',
    'mpass':'https://account.mojang.com/password'
  }
}

eel.init('page')

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
    mainThread = threading.Thread(target=eel.start,args=('login.html','log.html'),kwargs={'size':(600,400)})
    mainThread.start()
except OSError: pass

info('Start logging')

@eel.expose
def login(mcid,mcpw):
    try:
        if mcid == "" or mcpw == "":
            warn("Invalid ID or Password!")
        auth_token = pycraft.authentication.AuthenticationToken()
        auth_token.authenticate(mcid,mcpw)
        username = auth_token.profile.name
        info('Logined to ' + username)
        global rpc
        rpc.update(state='Select a Modpack',details='Logined to ' + username,large_image='favicon',large_text='Mystic Red Space',start=int(time.time()))
    except pex.YggdrasilError:
        error("Failed to login with " + mcid)
        return False
    return auth_token.client_token

rpc.update(state='Developing',details='MRS NEW LAUNCHER',large_image='favicon',large_text='Mystic Red Space',start=int(time.time()))