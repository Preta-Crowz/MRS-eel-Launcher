import json, os, pypresence, logging, time, threading, eel, datetime, platform, requests, subprocess
import pycraft
from pycraft import authentication
import pycraft.exceptions as pex
logger = logging.Logger("MRS")
now = str(datetime.datetime.now())
ndate = now[2:10].replace('-','')
ntime = now[11:17].replace(':','')
now = ndate+'_'+ntime
tfm = '%H:%M:%S'
fmt = '[%(levelname)s|%(asctime)s] > %(message)s'
formatter = logging.Formatter(fmt=fmt,datefmt=tfm)
file = logging.FileHandler(f'log/MRS_{now}.log')
file.setLevel(0)
file.setFormatter(formatter)
stream = logging.StreamHandler()
stream.setLevel(0)
stream.setFormatter(formatter)
logger.addHandler(file)
logger.addHandler(stream)
rpc = pypresence.Presence(490596975457337374)
rpc.connect()

baseDir = os.path.dirname(os.path.realpath(__file__))+'/'
launcher = {
  'name':'MRS Minecraft Launcher',
  'cn':'ZERO',
  'ver':{
    'major':0,
    'minor':0,
    'patch':0,
    'build':0,
    'str':"0.0.0.0"
  },
  'path':{
    'main':baseDir,
    'game':os.path.normpath(baseDir+'./games/'),
    'java':os.path.normpath(baseDir+'./runtime/'),
    'license':os.path.normpath(baseDir+'./LICENSE'),
    'updater':os.path.normpath(baseDir+'./updater.py'),
    'data':os.path.normpath(baseDir+'./data/'),
    'mclib':os.path.normpath(baseDir+'./lib/'),
    'mcver':os.path.normpath(baseDir+'./versions/'),
    'assets':os.path.normpath(baseDir+'./assets/')
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
    mainThread = threading.Thread(target=eel.start,args=('login.html','log.html'),kwargs={'size':(1200,800)})
    mainThread.start()
except OSError: pass

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
    return [auth_token.profile.name,auth_token.client_token]

rpc.update(state='Developing',details='MRS NEW LAUNCHER',large_image='favicon',large_text='Mystic Red Space',start=int(time.time()))

def getuuid(name):
    r = requests.get("https://api.mojang.com/users/profiles/minecraft/"+name).text
    return json.loads(r)["id"]

def libDir(name):
    l = name.split(":")
    l[0] = l[0].replace(".","/")
    return os.path.normpath(getLauncher()["path"]["mclib"]+"/{0}/{1}/{2}/{1}-{2}.jar".format(*l))

def getLibs(version):
    f = open(getLauncher()["path"]["mcver"]+"/"+version+".json")
    data = json.load(f)
    libs = []
    for lib in data["libraries"]:
        libs.append(libDir(lib["name"]))
    return ";".join(libs)

def getJava():
    javaw = os.path.normpath(getLauncher()["path"]["java"]+"/bin/javaw")
    if platform.system() == "Windows":
        return javaw + ".exe"
    return javaw

@eel.expose
def launch(version, name, memory=4):
    cmd = " ".join([
        getJava(),
        "-XX:HeapDumpPath=minecraft.heapdump",
        "-Djava.library.path=" + os.path.normpath(getLauncher()["path"]["main"]+"/temp"),
        "-Dminecraft.launcher.brand=mrs-eel-launcher",
        "-Dminecraft.launcher.version=" + getLauncher()["ver"]["str"],
        "-cp",
        getLibs(version),
        "-Xmx" + str(memory*1024) +"M",
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
        version.split(".")[0]+"."+version.split(".")[1],
        "--uuid",
        getuuid(name),
        "--accessToken",
        eel.getToken()(),
        "--userType",
        "mojang",
        "--versionType",
        "release"
        ])
    mc = subprocess.Popen(cmd)
    mc.wait()
    if mc.returncode:
        fatal(f"Client returned {mc.returncode}!")
        debug(cmd)
    return mc.returncode