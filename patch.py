import os
import launcher
import util
import subprocess
import zipfile
import whitelist
import modpack
from subprocess import Popen
from event import Event, ProgressEventArgs
from pmlauncher import pml, minecraft, mrule


# game start, download modpack
download_event = Event()


def downloadRuntime():
    path = os.path.normpath(launcher.path_temp+"/runtime.zip")
    util.download(launcher.url_runtime.format(os=mrule.osname)+"/runtime.zip", path)
    with zipfile.ZipFile(path) as f:
        f.extractall(os.path.normpath(launcher.path_runtime))


def getRuntime():
    if mrule.osname == "windows":
        bn = "javaw.exe"
    else:
        bn = "java"
    return os.path.normpath(launcher.path_runtime + "/bin/" + bn)


def patch_modpack(name):
    p = os.path.normpath(launcher.path_game + "/" + name)

    w = whitelist.WhiteList(p, name)
    files = w.getfiles()

    m = modpack.ModPackDownloader()
    m.event = download_event
    m.download(name, p, files)


def start_game(pack, session):
    pml.initialize(os.path.normpath(launcher.path_game + "/" + pack["name"]))
    minecraft.change_assets(launcher.path_assets)
    pml.downloadEventHandler = minecraft_eventhandler

    cmd = pml.startProfile(pack['profile'],
                            xmx_mb=1024,
                            session=session)

    subprocess.Popen(getRuntime() + " " + cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=pml.getGamePath(), shell=True)

    
def minecraft_eventhandler(x):
    fire(x.filename, x.currentvalue, x.maxvalue)


def fire(name, curr, all):
    download_event.fire(None, ProgressEventArgs(name, curr, all))