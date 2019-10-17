import datetime
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
import sys
import pycraft
import pycraft.exceptions as pex
from pycraft import authentication
from cefpython3 import cefpython as cef
from subprocess import Popen
import setup
now = str(datetime.datetime.now())
ndate = now[2:10].replace('-', '')
ntime = now[11:17].replace(':', '')
now = ndate + '_' + ntime
currToken = False

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
        'assets': os.path.normpath(baseDir + '/assets'),
        'index' : os.path.normpath(baseDir + '/assets/indexes'),
        'object' : os.path.normpath(baseDir + '/assets/objects'),
        'legacy' : os.path.normpath(baseDir + '/assets/virual/legacy'),
        'resources' : os.path.normpath(baseDir + '/resources')
    },
    'url': {
        'vers': 'https://launchermeta.mojang.com/mc/game/version_manifest.json',
        'list': 'https://api.mysticrs.tk/list',
        'info': 'https://api.mysticrs.tk/modpack',
        'white': 'https://api.mysticrs.tk/whitelist',
        'mpass': 'https://account.mojang.com/password',
        'osfolder': 'https://files.mysticrs.tk/{os}/',
        'file': 'https://files.mysticrs.tk/'
    }
}

def info(_):
    pass
def warn(_):
    pass
def logOutput(_):
    pass
def logOutput(_):
    pass
def updateRPC(**kwargs):
    pass

def mcArguments(version):
    data = loadVerData(version)
    if "minecraftArguments" in data.keys():
        args = data["minecraftArguments"]
    elif "arguments" in data.keys():
        args = data["arguments"]["game"]
        r = []
        for arg in args:
            if type(arg) == str:
                r.append(arg)
        args = " ".join(r)
    return args.replace("$","")

def libDir(o):
    path = o["path"]
    if path.find("lwjgl") + 1:
        return os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path) + ";" + \
               os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path.replace(".jar", "-natives-"+osType()+".jar"))
    elif path.find("java-objc-bridge") + 1 and osType == "osx":
        return os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path) + ";" + \
               os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path.replace(".jar", "-natives-"+osType()+".jar"))
    return os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path)

def saveToFile(fdir,data):
    if type(data) == dict:
        data = json.dumps(data).encode("utf8")
    elif type(data) == str:
        data = data.encode("utf8")
    elif type(data) == bytes:
        pass
    else:
        raise TypeError("Unsupported Type")
    mkLoop(os.path.dirname(fdir))
    return open(fdir, "wb").write(data)
>>>>>>> f12105be709d7487f3ab1255fc9e3735dfec2184

def loadFromWeb(url):
    return json.loads(requests.get(url).text)

def getuuid(name):
    r = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name).text
    return json.loads(r)["id"]
    
def isTokenVaild(token):
    auth_token = authentication.AuthenticationToken(token[0],token[2],token[3])
    return bool(auth_token.validate())

def downloadRuntime():
    launcher = getLauncher()
    path = os.path.normpath(launcher["path"]["temp"]+"/runtime.zip")
    download(path, launcher['url']['osfolder'].format(os=osType())+"/runtime.zip")
    with zipfile.ZipFile(path) as f:
        f.extractall(os.path.normpath(launcher["path"]["runtime"]))

def isLegacy(version):
    try:
        if int(version.split(".")[1]) > 8: return 0
        elif int(version.split(".")[1]) == 8: return 2
    except IndexError:
        rmat = re.match("(?P<year>\d{2})w\d{2}.", version)
        if int(rmat["year"]) > 14: return 0
        elif int(rmat["year"]) == "14": return 2
    return 1

def mkLoop(fdir):
    if os.path.exists(fdir):
        return
    try:
        os.mkdir(fdir)
    except:
        mkLoop(os.path.dirname(fdir))
        os.mkdir(fdir)
        

def download(fdir,url):
    dirpath = os.path.dirname(fdir)
    mkLoop(dirpath)
    with open("log.log","a") as ab:
        ab.write(fdir+"\r\n")
    response = requests.get(url, stream=True)
    if int(response.status_code / 100) is not 2:
        return  # TODO : Raise Exception

    with open(fdir, 'wb') as f:
        shutil.copyfileobj(response.raw, f)

def extract(nativeFile):
    zf = zipfile.ZipFile(nativeFile)
    zf.extractall(os.path.normpath(getLauncher()["path"]["main"] + "/extracts"))
    zf.close()
    
def downloadRuntime():
    launcher = getLauncher()
    path = os.path.normpath(launcher["path"]["temp"]+"/runtime.zip")
    download(path, launcher['url']['osfolder'].format(os=osType())+"/runtime.zip")
    with zipfile.ZipFile(path) as f:
        f.extractall(os.path.normpath(launcher["path"]["runtime"]))
        
def downloadJar(version):
    path = os.path.normpath(getLauncher()["path"]["mcver"]+"/"+version+".jar")
    url = loadVerData(version)["downloads"]["client"]["url"]
    download(path, url)
    
def loadAssetsIndex(version):
    baseData = loadVerData(version)
    vid = baseData["assetIndex"]["id"]
    path = os.path.normpath(getLauncher()["path"]["assets"]+"/indexes/"+vid+".json")
    if not os.path.exists(path):
        downloadAssetsIndex(version)
    return json.load(open(path))

def downloadAssetsIndex(version):
    baseData = loadVerData(version)
    vid = baseData["assetIndex"]["id"]
    return download(os.path.normpath(getLauncher()["path"]["assets"]+"/indexes/"+vid+".json"), baseData["assetIndex"]["url"])

def downloadAssets(index):
    isMapResource = False
    m = index.get("map_to_resources")
    if m and m == True:
        isMapResource = True

    isVirtual = False  # check virtual
    v = index.get("virtual")
    if v and v == True:
        isVirtual = True

    items = list(index.get("objects").items())
    count = len(items)

    for i in range(0, count):
        key = items[i][0]
        value = items[i][1]

        hash = value.get("hash")
        hashName = hash[:2] + "/" + hash
        hashPath = os.path.normpath(getLauncher()["path"]["object"] + "/" + hashName)
        hashUrl = "http://resources.download.minecraft.net/" + hashName

        if not os.path.isfile(hashPath):
            info("Downloading " + key + "(" + str(now) + "/" + str(count) + ")")
            download(hashPath, hashUrl)

        if isVirtual:
            resPath = os.path.normpath(getLauncher()["path"]["object"] + "/" + key)
            print(resPath)

            if not os.path.isfile(resPath):
                mkLoop(os.path.dirname(resPath))
                shutil.copyfile(hashPath, resPath)

        if isMapResource:
            resPath = os.path.normpath(getLauncher()["path"]["resources"] + "/" + key)
            print(resPath)

            if not os.path.isfile(resPath):
                mkLoop(os.path.dirname(resPath))
                shutil.copyfile(hashPath, resPath)
                
def loadVerData(version):
    fn = os.path.normpath(getLauncher()["path"]["mcver"]+"/"+version+".json")
    if os.path.exists(fn):
        return json.load(open(fn,"r"))
    else:
        data = getVerData(version)
        saveToFile(fn, data)
        return data
        
vdata = None
def getVerData(version):
    global vdata
    if vdata is None:
        vdata = loadFromWeb(getLauncher()["url"]["vers"])["versions"]
    return loadFromWeb(list(filter((lambda v: v["id"] == version),vdata))[0]["url"])

def getRuntime(noArgs=False):
    bn = "java" if osType == "osx" else "javaw"
    runtime = os.path.normpath(getLauncher()["path"]["runtime"] + "/bin/" + bn)
    if noArgs:
        return runtime + (".exe" if osType() == "windows" else "")
    elif osType() == "windows":
        return runtime + ".exe -XX:HeapDumpPath=minecraft.heapdump"
    elif osType() == "osx":
        return runtime + " -XstartOnFirstThread"
    return runtime
    
def jarExists(version):
    path = os.path.normpath(getLauncher()["path"]["mcver"]+"/"+version+".jar")
    return os.path.exists(path)
    
def assetsIndexExist(version):
    baseData = loadVerData(version)
    vid = baseData["assetIndex"]["id"]
    return os.path.exists(os.path.normpath(getLauncher()["path"]["assets"]+"/indexes/"+vid+".json"))

def libCheck(version):
    ok = True
    index = loadVerData(version)["libraries"]
    for o in index:
        k = o["downloads"].keys()
        if "artifact" in k:
            path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["artifact"]["path"])
            if not os.path.exists(path):
                ok = False
        if "classifiers" in k:
            if osType() == "windows":
                if ("natives-windows" in o["downloads"]["classifiers"].keys()): ost = "windows"
                else: ost = "windows-64"
            else: ost = osType()
            if "natives-"+ost in o["downloads"]["classifiers"].keys():
                path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["classifiers"]["natives-"+ost]["path"])
                if not os.path.exists(path):
                    ok = False
            
    return ok

def downloadLibs(version):
    index = loadVerData(version)["libraries"]
    count = len(index)
    now = 1
    for o in index:
        k = o["downloads"].keys()
        if "artifact" in k:
            path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["artifact"]["path"])
            if not os.path.exists(path):
                info("Downloading " + o["name"] + "(" + str(now) + "/" + str(count) + ")")
                url = o["downloads"]["artifact"]["url"]
                download(path, url)
        if "classifiers" in k:
            if osType() == "windows":
                if ("natives-windows" in o["downloads"]["classifiers"].keys()): ost = "windows"
                elif ("natives-windows-64" in o["downloads"]["classifiers"].keys()): ost = "windows-64"
                else: continue
            else: ost = osType()
            if "natives-"+ost in o["downloads"]["classifiers"].keys():
                path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["classifiers"]["natives-"+ost]["path"])
                url = o["downloads"]["classifiers"]["natives-"+ost]["url"]
                if not os.path.exists(path):
                    download(path, url)
            else: pass
        now += 1
    
def osType():
    base = platform.system()
    if base == "Windows":
        return "windows"
    elif base == "Darwin":
        return "osx"
    else:
        return "linux"

def getLibs(version):
    f = open(getLauncher()["path"]["mcver"] + "/" + version + ".json")
    data = json.load(f)
    libs = []
    for lib in data["libraries"]:
        if not "artifact" in lib["downloads"].keys(): continue
        libs.append(libDir(lib["downloads"]["artifact"]))
        for l in libDir(lib["downloads"]["artifact"]).split(";"):
            if (l.find("natives") != -1):
                try:
                    extract(l)
                except:
                    pass

    return ";".join(libs)
    
def getLauncher():
    global launcher
    return launcher

def launch(version, name, modpack=False, memory=1):
    gp = modpack if modpack else version
    if not modpack:
        if re.match("\d\dw\d\d.|1\.\d{1,2}(\.\d{1,2})?-pre( release )?\d{1,2}?", version):
            modpack = "Snapshot " + version
            vtype = "snapshot"
            vver = version
        else:
            modpack = "Vanilla " + version
            vtype = "release"
            vver = version
    else:
        vtype = "Forge"
        vver = version.split("-")[0]

    Legacy = isLegacy(vver)

    if Legacy:
        path = os.path.normpath(getLauncher()["path"]["data"] + "/natives.zip")
        if not os.path.exists(path):
            download(path, getLauncher()["url"]["osfolder"].format(os=osType())+"/natives.zip")
        extract(path)

    if not os.path.exists(getRuntime(True)):
        downloadRuntime()

    if not jarExists(vver):
        downloadJar(vver)

    if not assetsIndexExist(vver):
        downloadAssetsIndex(vver)

    assetVer = loadAssetsIndex(version)
    downloadAssets(assetVer)


    if not libCheck(vver):
        downloadLibs(vver)

    cmd = " ".join([
        getRuntime(),
        "-Djava.library.path=" + os.path.normpath(getLauncher()["path"]["main"] + "/extracts"),
        "-Dminecraft.launcher.brand=mrs-eel-launcher",
        "-Dminecraft.launcher.version=" + getLauncher()["ver"]["str"],
        "-Xmx" + str(memory * 1024) + "M",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
        "-Dlog4j.configurationFile=" + os.path.normpath(getLauncher()["path"]["assets"] + "/client-1.12.xml"),
        "-cp",
        getLibs(version) + ";" + os.path.normpath(getLauncher()["path"]["mcver"] + "/" + vver + ".jar"),
        "net.minecraft.client.main.Main",
        mcArguments(version).format(auth_player_name=name, version_name=vver,
            game_directory=os.path.normpath(getLauncher()["path"]["game"]),
            assets_root=getLauncher()["path"]["assets"],
            assets_index_name=getVerData(version)["assets"],
            auth_uuid=getuuid(name),
            auth_access_token=currToken,
            user_type="mojang",
            version_type=vtype,
            user_properties="{}", 
            auth_session=currToken, 
            game_assets=getLauncher()["path"]["legacy"])
    ])
    with open("log.log","a") as ab:
        mc = subprocess.Popen(cmd, stdout=ab, stderr=subprocess.STDOUT, encoding="utf8")
    updateRPC(state='Playing MRS', details=modpack, large_image='favicon', large_text='Mystic Red Space',
               start=int(time.time()))
    with mc.stdout as gameLog:
        logOutput(gameLog)
    if mc.returncode:
        warn(f"Client returned {mc.returncode}!")
    return mc.returncode
    
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
os.environ["pagedir"] = os.getcwd()+r'\page'
if osType() == "windows":
    os.environ["pagedir"] = os.getcwd()+r'\page'
    server = Popen(["./caddy_win","-conf","caddyfile"])
elif osType() == "osx":
    os.environ["pagedir"] = os.getcwd()+r'/page'
    server = Popen(["./caddy_mac","-conf","caddyfile"])
elif osType() == "linux":
    os.environ["pagedir"] = os.getcwd()+r'/page'
    server = Popen(["./caddy_linux","-conf","caddyfile"])
cef.Initialize(settings={'cache_path':os.getcwd()+r'\cache'})
browser = cef.CreateBrowserSync(url="http://localhost:12345/login.html",
                      window_title="MRS Launcher")
if osType() == "windows":
    cef.WindowUtils.SetIcon
bindings = cef.JavascriptBindings()
bindings.SetFunction('isTokenVaild',isTokenVaild)
bindings.SetFunction('login',login)
bindings.SetFunction('launch',launch)
browser.SetJavascriptBindings(bindings)
cef.MessageLoop()
server.terminate()
cef.Shutdown()


