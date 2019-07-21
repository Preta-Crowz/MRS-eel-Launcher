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
        'assets': os.path.normpath(baseDir + '/assets')
    },
    'url': {
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

@eel.expose
def login(mcid, mcpw):
    try:
        if mcid == "" or mcpw == "":
            warn("Invalid ID or Password!")
        auth_token = pycraft.authentication.AuthenticationToken()
        auth_token.authenticate(mcid, mcpw)
        username = auth_token.profile.name
        info('Logined to ' + username)
        global rpc
        rpc.update(state='Selectting a Modpack', details='Logined to ' + username, large_image='favicon',
                   large_text='Mystic Red Space')
    except pex.YggdrasilError:
        error("Failed to login with " + mcid)
        return False
    global currToken
    currToken = auth_token.access_token
    return [auth_token.profile.name, auth_token.client_token, auth_token.access_token]


@eel.expose
def isTokenVaild():
    auth_token = pycraft.AuthenticationToken(*(eel.loadToken()()))
    return bool(auth_token.validate())


@eel.expose
def refreshToken():
    global currToken, auth_token
    auth_token = pycraft.AuthenticationToken(*(eel.loadToken()()))
    auth_token.refresh()
    currToken = auth_token.access_token
    return [auth_token.profile.name, auth_token.client_token, auth_token.access_token]


rpc.update(state='Developing', details='MRS NEW LAUNCHER', large_image='favicon', large_text='Mystic Red Space',
           start=int(time.time()))


def getuuid(name):
    r = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name).text
    return json.loads(r)["id"]


def libDir(o):
    path = o["path"]
    if path.find("lwjgl") + 1:
        return os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path) + ";" + \
               os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path.replace(".jar", "-natives-"+osType()+".jar"))
    elif path.find("java-objc-bridge") + 1 and osType == "osx":
        return os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path) + ";" + \
               os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path.replace(".jar", "-natives-"+osType()+".jar"))
    return os.path.normpath(getLauncher()["path"]["mclib"] + "/" + path)


def getLibs(version):
    f = open(getLauncher()["path"]["mcver"] + "/" + version + ".json")
    data = json.load(f)
    libs = []
    for lib in data["libraries"]:
        try:
            libs.append(libDir(lib["downloads"]["artifact"]))
        except:
            pass
    return ";".join(libs)


def getJava(noArgs=False):
    javaw = os.path.normpath(getLauncher()["path"]["runtime"] + "/bin/javaw")
    if noArgs:
        return javaw + (".exe" if osType() == "windows" else "")
    elif osType() == "windows":
        return javaw + ".exe -XX:HeapDumpPath=minecraft.heapdump"
    elif osType() == "osx":
        return javaw + " -XstartOnFirstThread"
    return javaw
    


nextLog = False
nLogThread = ""
nLogLevel = ""
nextOutput = ""


def logOutput(pipe):
    for line in iter(pipe.readline, b'\n'):
        global nextLog, nLogThread, nLogLevel, nextOutput
        lastOutput = line.decode()
        if lastOutput == "": return
        if lastOutput.startswith("AL lib"): return
        baseRegex = r'<log4j:Event logger=".+" timestamp="\d+" level="(?P<level>.+)" thread="(?P<thread>.+)">'
        rmatch = re.search(baseRegex, lastOutput)
        if rmatch:
            if rmatch["level"] == "DEBUG":
                nextLog = debug
            elif rmatch["level"] == "INFO":
                nextLog = info
            elif rmatch["level"] == "WARN":
                nextLog = warn
            elif rmatch["level"] == "ERROR":
                nextLog = error
            elif rmatch["level"] == "FATAL":
                nextLog = fatal
            else:
                continue
            nLogThread = rmatch["thread"]
            nLogLevel = rmatch["level"]
            continue
        elif nextLog:
            passRegex = r"</log4j:Event>|Narrator library"
            if re.search(passRegex, lastOutput): continue
            logRegex = r"<log4j:Message><!\[CDATA\[(?P<output>.+)\]\]>(</log4j:Message>)?"
            output = re.search(logRegex, lastOutput)
            end = r"</log4j:Message>"
            outEnd = re.search(end, lastOutput)
            if output and outEnd:
                nextLog("[" + nLogThread + "/" + nLogLevel + "] " + output["output"])
                nextOutput = ""
            elif output:
                nextOutput += lastOutput
            else:
                nextLog("[" + nLogThread + "/" + nLogLevel + "] " + nextOutput + lastOutput)
                nextOutput = ""
            continue
        else:
            debug(lastOutput)

def loadFromWeb(url):
    return json.loads(requests.get(url).text)

def getBaseVer(forgedVersion):
    return forgedVersion.split("-")[0]

def getVerData(version):
    urlData = loadFromWeb("https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/"+version+"/version.json")
    return loadFromWeb(urlData["url"])

def loadVerData(version):
    fn = os.path.normpath(getLauncher()["path"]["mcver"]+"/"+version+".json")
    if os.path.exists(fn):
        return json.load(open(fn,"r"))
    else:
        data = getVerData(version)
        saveToFile(fn, data)
        return data

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

def mkLoop(fdir):
    if os.path.exists(fdir):
        return
    try:
        os.mkdir(fdir)
    except:
        mkLoop(os.path.dirname(fdir))
        os.mkdir(fdir)

def download(fdir,url):
    return saveToFile(fdir, requests.get(url).content)

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

def assetsIndexExist(version):
    baseData = loadVerData(version)
    vid = baseData["assetIndex"]["id"]
    return os.path.exists(os.path.normpath(getLauncher()["path"]["assets"]+"/indexes/"+vid+".json"))

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

def assetsCheck(version):
    index = loadAssetsIndex(version)["objects"]
    for k in index:
        fh = index[k]["hash"]
        path = os.path.normpath(getLauncher()["path"]["assets"]+"/objects/"+fh[0:2]+"/"+fh)
        if not os.path.exists(path):
            return False
    return True

def downloadAssets(version):
    index = loadAssetsIndex(version)["objects"]
    count = len(list(index.keys()))
    now = 1
    for k in index:
        fh = index[k]["hash"]
        path = os.path.normpath(getLauncher()["path"]["assets"]+"/objects/"+fh[0:2]+"/"+fh)
        if not os.path.exists(path):
            info("Downloading " + k + "(" + str(now) + "/" + str(count) + ")")
            url = "http://resources.download.minecraft.net/"+fh[0:2]+"/"+fh
            download(path, url)
        now += 1

def jarExists(version):
    path = os.path.normpath(getLauncher()["path"]["mcver"]+"/"+version+".jar")
    return os.path.exists(path)

def downloadJar(version):
    path = os.path.normpath(getLauncher()["path"]["mcver"]+"/"+version+".jar")
    url = loadVerData(version)["downloads"]["client"]["url"]
    download(path, url)

def libCheck(version):
    index = loadVerData(version)["libraries"]
    for o in index:
        try:
            path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["artifact"]["path"])
        except:
            continue
        if not os.path.exists(path):
            return False
        if "classifiers" in o["downloads"].keys():
            if "natives-"+osType() in o["downloads"]["classifiers"].keys():
                path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["classifiers"]["natives-"+osType()]["path"])
                extract(path)
                if not os.path.exists(path):
                    return False
            
    return True

def downloadLibs(version):
    index = loadVerData(version)["libraries"]
    count = len(index)
    now = 1
    for o in index:
        try:
            path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["artifact"]["path"])
        except:
            error("Failed to download lib :" + o["name"])
            warn("Game will be launch unstable!")
            continue
        if not os.path.exists(path):
            info("Downloading " + o["name"] + "(" + str(now) + "/" + str(count) + ")")
            url = o["downloads"]["artifact"]["url"]
            download(path, url)
        if "classifiers" in o["downloads"].keys():
            if "natives-"+osType() in o["downloads"]["classifiers"].keys():
                path = os.path.normpath(getLauncher()["path"]["mclib"]+"/"+o["downloads"]["classifiers"]["natives-"+osType()]["path"])
                url = o["downloads"]["classifiers"]["natives-"+osType()]["url"]
                if not os.path.exists(path):
                    download(path, url)
        now += 1
    
def osType():
    base = platform.system()
    if base == "Windows":
        return "windows"
    elif base == "Darwin":
        return "osx"
    else:
        return "linux"

def extract(nativeFile):
    zf = zipfile.ZipFile(nativeFile)
    zf.extractall(os.path.normpath(getLauncher()["path"]["main"] + "/extracts"))
    zf.close()


@eel.expose
def launch(version, name, modpack=False, memory=1):
    if not modpack:
        if re.match("\d\dw\d\d.|1\.\d{1,2}(\.\d{1,2})?-pre( release )\d{1,2}?", version):
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

    if not os.path.exists(getJava(True)):
        warn("Runtime not found! Downloading new runtime..")
        downloadRuntime()

    if not jarExists(vver):
        warn("Jar file not found! Downloading new jar..")
        downloadJar(vver)

    if not assetsIndexExist(vver):
        warn("Assets Index not found! Downloading new index..")
        downloadAssetsIndex(vver)

    if not assetsCheck(vver):
        warn("Some assets not found! Downloading new assets..")
        downloadAssets(vver)

    if not libCheck(vver):
        warn("Some libraries not found! Downloading new libraries..")
        downloadLibs(vver)


    info("Launching " + modpack + "!")
    cmd = " ".join([
        getJava(),
        "-Djava.library.path=" + os.path.normpath(getLauncher()["path"]["main"] + "/extracts"),
        "-Dminecraft.launcher.brand=mrs-eel-launcher",
        "-Dminecraft.launcher.version=" + getLauncher()["ver"]["str"],
        "-cp",
        getLibs(version) + ";" + os.path.normpath(getLauncher()["path"]["mcver"] + "/" + vver + ".jar"),
        "-Xmx" + str(memory * 1024) + "M",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
        "-Dlog4j.configurationFile=" + os.path.normpath(getLauncher()["path"]["assets"] + "/client-1.12.xml"),
        "net.minecraft.client.main.Main",
        mcArguments(version).format(auth_player_name=name, version_name=version,
            game_directory=os.path.normpath(getLauncher()["path"]["game"] + "/" + version),
            assets_root=getLauncher()["path"]["assets"],
            assets_index_name=getVerData(version)["assets"],
            auth_uuid=getuuid(name), auth_access_token=currToken, user_type="mojang", version_type=vtype,
            user_properties="{}")
    ])
    debug(cmd)
    mc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rpc.update(state='Playing MRS', details=modpack, large_image='favicon', large_text='Mystic Red Space',
               start=int(time.time()))
    with mc.stdout as gameLog:
        logOutput(gameLog)
    if mc.returncode:
        warn(f"Client returned {mc.returncode}!")
    return mc.returncode

def downloadRuntime():
    launcher = getLauncher()
    path = os.path.normpath(launcher["path"]["temp"]+"/runtime.zip")
    download(path, launcher['url']['runtime'].format(os=osType()))
    with zipfile.ZipFile("path") as launcher["path"]["runtime"]:
        f.extractall()
