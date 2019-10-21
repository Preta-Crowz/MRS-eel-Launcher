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
    global setting_obj, default_setting
    try:
        if os.path.isfile(launcher.path_setting):
            content = util.readfile(launcher.path_setting)
            setting_obj = json.loads(content)

            if setting_obj is None:
                setting_obj = default_setting
        else:
            setting_obj = default_setting
    except:
        setting_obj = default_setting
    print(setting_obj)

def get(key):
    global setting_obj
    if setting_obj is None:
        load()
    print(setting_obj)
    return setting_obj.get(key)


def set(key, val):
    global setting_obj
    if setting_obj is None:
        load()

    setting_obj[key] = val


def save():
    global setting_obj
    util.writefile(launcher.path_setting, json.dumps(setting_obj))
