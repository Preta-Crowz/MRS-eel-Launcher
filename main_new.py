import sys
import os
import pycraft
import pycraft.exceptions as pex
from pycraft import authentication
from cefpython3 import cefpython as cef
from subprocess import Popen

def isTokenVaild(token):
    auth_token = authentication.AuthenticationToken(token[0],token[1],token[2])
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
    js_callback.Call([auth_token.profile.name, auth_token.client_token, auth_token.access_token])

#sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
os.environ["pagedir"] = os.getcwd()+r'\page'
server = Popen(["caddy","-conf","caddyfile"])
cef.Initialize(settings={'cache_path':os.getcwd()+r'\cache'})
browser = cef.CreateBrowserSync(url="http://localhost:12345/login.html",
                      window_title="MRS Launcher")
cef.WindowUtils.SetIcon
bindings = cef.JavascriptBindings()
bindings.SetFunction('isTokenVaild',isTokenVaild)
bindings.SetFunction('login',login)
browser.SetJavascriptBindings(bindings)
cef.MessageLoop()
server.terminate()
cef.Shutdown()


