import sys
import os
import pycraft
import pycraft.exceptions as pex
from pycraft import authentication
from cefpython3 import cefpython as cef
import aiohttp

def isTokenVaild():
    auth_token = pycraft.AuthenticationToken(browser.ExecuteFunction('loadToken'))
    print(auth_token)
    return bool(auth_token.validate())
    
def login(mcid, mcpw , js_callback=None):
    try:
        if mcid == "" or mcpw == "":
            warn("Invalid ID or Password!")
        auth_token = pycraft.authentication.AuthenticationToken()
        auth_token.authenticate(mcid, mcpw)
        username = auth_token.profile.name
        print('Logined to ' + username)
    except pex.YggdrasilError:
        print("Failed to login with " + mcid)
        return False
    global currToken
    currToken = auth_token.access_token
    js_callback.Call([auth_token.profile.name, auth_token.client_token, auth_token.access_token],os.getcwd())

#sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
cef.Initialize()
browser = cef.CreateBrowserSync(url="file://{}/page/login.html".format(os.getcwd()),
                      window_title="MRS Launcher",settings={'web_security_disabled':True})
bindings = cef.JavascriptBindings()
bindings.SetFunction('isTokenVaild',isTokenVaild)
bindings.SetFunction('login',login)
browser.SetJavascriptBindings(bindings)
cef.MessageLoop()
cef.Shutdown()


