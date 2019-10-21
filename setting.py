import json
import os
import launcher
import util

default_setting = {
    'xmx' : 4096,
    'useCustomJVM' : False,
    'jvm' : ''
}
setting_obj = None

def load():
    global setting_obj
    try:
        if os.path.isfile(launcher.path_setting):
            content = util.readfile(launcher.path_setting)
            setting_obj = json.loads(content)
        else:
            setting_obj = default_setting
    except:
        setting_obj = default_setting

def get(key):
    global setting_obj

    if setting_obj == None:
        load()

    return setting_obj.get(key)


def set(key, val):
    global setting_obj

    if setting_obj == None:
        load()

    setting_obj[key] = val


def save():
    global setting_obj
    util.writefile(launcher.path_setting, json.dumps(setting_obj))

