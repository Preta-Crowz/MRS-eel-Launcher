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
        'game': os.path.normpath(baseDir + '/games'),
        'java': os.path.normpath(baseDir + '/runtime'),
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
        'mpass': 'https://account.mojang.com/password'
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
def login(mcid, mcpw, saveInfo):
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
    if saveInfo:
        print("Save info for " + username + " to mai file")
        saveToFile(os.path.normpath(getLauncher()["path"]["data"] + "/account.mai"), {"mail":mcid,"pass":mcpw})
    return [auth_token.profile.name, auth_token.client_token]


rpc.update(state='Developing', details='MRS NEW LAUNCHER', large_image='favicon', large_text='Mystic Red Space',
           start=int(time.time()))


def getuuid(name):
    r = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name).text
    return json.loads(r)["id"]


def libDir(name):
    l = name.split(":")
    l[0] = l[0].replace(".", "/")
    if l[1].startswith("lwjgl") and platform.system() == "Windows":
        return os.path.normpath(getLauncher()["path"]["mclib"] + "/{0}/{1}/{2}/{1}-{2}.jar".format(*l)) + ";" + \
               os.path.normpath(getLauncher()["path"]["mclib"] + "/{0}/{1}/{2}/{1}-{2}-natives-windows.jar".format(*l))
    return os.path.normpath(getLauncher()["path"]["mclib"] + "/{0}/{1}/{2}/{1}-{2}.jar".format(*l))


def getLibs(version):
    f = open(getLauncher()["path"]["mcver"] + "/" + version + ".json")
    data = json.load(f)
    libs = []
    for lib in data["libraries"]:
        libs.append(libDir(lib["name"]))
    return ";".join(libs)


def getJava():
    javaw = os.path.normpath(getLauncher()["path"]["java"] + "/bin/javaw")
    if platform.system() == "Windows":
        return javaw + ".exe"
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
    fn = os.path.normpath(getLauncher()["path"]["assets"]+"/basedatas/"+version+".json")
    if os.path.exists(fn):
        return json.load(open(fn,"r"))
    else:
        data = getVerData(version)
        saveToFile(fn, data)
        return data

def saveToFile(fdir,data):
    if type(data) == dict:
        data = json.dumps(data)
    return open(fdir, "wb").write(data.encode("utf8"))

def download(fdir,url):
    return saveToFile(fdir, requests.get(url).content)

def downloadAssets(version):
    baseData = loadVerData(version)
    vid = baseData["assetIndex"]["id"]
    download(os.path.normpath(getLauncher["path"]["assets"]+"/indexes/"+vid+".json"), baseData["assetIndex"]["url"])


@eel.expose
def launch(version, name, modpack=False, memory=1):
    if not modpack: modpack = "Vanilla " + version
    info("Launching " + modpack + "!")
    cmd = " ".join([
        getJava(),
        "-XX:HeapDumpPath=minecraft.heapdump",
        "-Djava.library.path=" + os.path.normpath(getLauncher()["path"]["main"] + "/temp"),
        "-Dminecraft.launcher.brand=mrs-eel-launcher",
        "-Dminecraft.launcher.version=" + getLauncher()["ver"]["str"],
        "-cp",
        getLibs(version) + ";" + os.path.normpath(getLauncher()["path"]["mcver"] + "/" + version + ".jar"),
        "-Xmx" + str(memory * 1024) + "M",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
        "-Dlog4j.configurationFile=" + os.path.normpath(getLauncher()["path"]["assets"] + "/client-1.12.xml"),
        "net.minecraft.client.main.Main",
        "--username",
        name,
        "--version",
        version,
        "--gameDir",
        os.path.normpath(getLauncher()["path"]["game"] + "/" + version),
        "--assetsDir",
        getLauncher()["path"]["assets"],
        "--assetIndex",
        version.split(".")[0] + "." + version.split(".")[1],
        "--uuid",
        getuuid(name),
        "--accessToken",
        currToken,
        "--userType",
        "mojang",
        "--versionType",
        "release"
    ])
    mc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rpc.update(state='Playing MRS', details=modpack, large_image='favicon', large_text='Mystic Red Space',
               start=int(time.time()))
    with mc.stdout as gameLog:
        logOutput(gameLog)
    if mc.returncode:
        fatal(f"Client returned {mc.returncode}!")
        debug(cmd)
    return mc.returncode
