import json
import os
import launcher
import codec

default_setting = {
    'xmx' : 4096,
    'useCustomJVM' : False,
    'jvm' : ''
}
setting_obj = None

def load():
    global setting_obj
    if os.path.isfile(launcher.path_setting):
        f = codec.open(launcher.path_setting, 'r', encoding='utf8')
        content = f.read()
        setting_obj = json.loads(content)
        f.close()
    else:
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
    f = codec.open(launcher.path_setting, 'w', encoding='utf8'
    f.write(json.dump(setting_obj))
    f.close()
