import datetime
import json
import logging
import os
import platform
import pypresence
import re
import requests
import threading
import time
import sys
import threading
import pycraft
import pycraft.exceptions as pex
import modpack
from subprocess import Popen
from pmlauncher import mlogin
from pycraft import authentication
from cefpython3 import cefpython as cef
import launcher
import util
import patch
import setting


now = str(datetime.datetime.now())
ndate = now[2:10].replace('-', '')
ntime = now[11:17].replace(':', '')
now = ndate + '_' + ntime
currToken = False


def info(_):
    pass
def warn(_):
    pass
def logOutput(_):
    pass
def updateRPC(**kwargs):
    pass


def isTokenVaild(token):
    auth_token = authentication.AuthenticationToken(token[0],token[2],token[3])
    return bool(auth_token.validate())


def eventhandler(x):
    print(f"{x.name} : {x.current} / {x.allcount}")


def launch(version, name):
    session = mlogin.session()
    session.access_token = currToken
    session.uuid = "asdf"
    session.username = name

    t = threading.Thread(target=start, args=(version, session))
    t.daemon = True
    t.start()

    updateRPC(state='Playing MRS', details="", large_image='favicon', large_text='Mystic Red Space',
              start=int(time.time()))


def start(version, session):
    patch.download_event.clear_handler()
    patch.download_event.add_handler(eventhandler)

    packs = modpack.getlist()
    p = None
    for i in packs:
        if i["name"] == version:
            p = i
            break

    if p == None:
        raise ValueError("Cannot find modpack")
    
    patch.patch_modpack(p["name"])
    patch.start_game(p, session)
    
    
def login(mcid, mcpw ,js_callback=None):
    try:
        if mcid == "" or mcpw == "":
            pass
        auth_token = pycraft.authentication.AuthenticationToken()
        auth_token.authenticate(mcid, mcpw)
        username = auth_token.profile.name
        print('Logined to ' + username)
    except pex.YggdrasilError:
        print("Failed to login with " + mcid)
        return False
    global currToken
    currToken = auth_token.access_token
    js_callback.Call([auth_token.profile.name, auth_token.profile.id_, auth_token.client_token, auth_token.access_token])
    

#sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
os.environ["pagedir"] = os.path.normpath(os.getcwd()+'/page')
server = Popen(["./caddy_" + util.osType(), "-conf", "caddyfile"])

cef.Initialize(settings={'cache_path':launcher.path_temp})
browser = cef.CreateBrowserSync(url="http://localhost:12345/login.html",
                      window_title="MRS Launcher")
if util.osType() == "windows":
    cef.WindowUtils.SetIcon
bindings = cef.JavascriptBindings()
bindings.SetFunction('isTokenVaild',isTokenVaild)
bindings.SetFunction('login',login)
bindings.SetFunction('launch',launch)
browser.SetJavascriptBindings(bindings)
cef.MessageLoop()

# Deinitialize
server.terminate()
setting.save()
cef.Shutdown()

