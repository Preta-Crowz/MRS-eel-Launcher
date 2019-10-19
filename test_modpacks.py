import modpack
import whitelist
from pprint import pprint
import util
import os
import patch
from pmlauncher import mlogin

def eventhandler(x):
    print(f"{x.name} : {x.current} / {x.allcount}")


def launch(version, name):
    patch.download_event.clear_handler()
    patch.download_event.add_handler(eventhandler)

    session = mlogin.session()
    session.access_token = "asdf"
    session.uuid = "asdf"
    session.username = name

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

launch("MRS Builders", "hi")