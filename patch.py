import os
import launcher
import util
import subprocess
import zipfile
import whitelist
import modpack
from subprocess import Popen
from event import Event, ProgressEventArgs
from pmlauncher import pml, minecraft, mrule, mlaunchoption
import setting


# game start, download modpack
download_event = Event()

def getRuntime():
    if mrule.osname == "windows":
        bn = "javaw.exe"
    else:
        bn = "java"
    runtime = os.path.normpath(launcher.path_runtime + "/bin/" + bn)

    if not os.path.isfile(runtime):
        zippath = os.path.normpath(launcher.path_temp + "/runtime.zip")
        util.download(launcher.url_runtime.format(os=mrule.osname)+"/runtime.zip", zippath)

        with zipfile.ZipFile(zippath) as f:
            f.extractall(os.path.normpath(launcher.path_runtime))

    return runtime


def patch_modpack(name, force=False):
    p = os.path.normpath(launcher.path_game + "/" + name)

    m = modpack.ModPackDownloader()
    w = whitelist.WhiteList(p, name)

    mpath = os.path.normpath(p + "/modpack.json")
    wpath = os.path.normpath(p + "/whitelist.json")

    if not check_file_equal(mpath, m.res) or not check_file_equal(wpath, w.res) or force:
        files = w.getfiles()
        m.event = download_event
        m.download(name, p, files)
        w.filtering(files)

        util.writefile(mpath, m.res)
        util.writefile(wpath, w.res)


def check_file_equal(path, content):
    file = util.readfile(path)
    return file == content


def start_game(pack, session):
    pml.initialize(os.path.normpath(launcher.path_game + "/" + pack["name"]))
    minecraft.change_assets(launcher.path_assets)
    pml.downloadEventHandler = minecraft_eventhandler

    option = mlaunchoption.launchoption()
    option.xmx_mb = setting.get("xmx")
    option.session = session
    
    if setting.get("useCustomJVM"):
        option.jvm_arg = setting.get("jvm")

    cmd = pml.startProfile(pack['profile'], launchoption=option)

    print(cmd)

    mc = subprocess.Popen(getRuntime() + " " + cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=pml.getGamePath(), shell=True)

    # write output
    with mc.stdout as gameLog:
        while True:
            line = gameLog.readline()
            if not line:
                break
            print(line)

    
def minecraft_eventhandler(x):
    fire(x.filename, x.currentvalue, x.maxvalue)


def fire(name, curr, all):
    download_event.fire(None, ProgressEventArgs(name, curr, all))
