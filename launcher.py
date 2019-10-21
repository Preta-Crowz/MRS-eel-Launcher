import os

def f(path):
    path = os.path.normpath(path)
    m(os.path.dirname(path)
    return path

def m(path):
    path = os.path.normpath(path)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

name = 'MRS Minecraft Launcher'

ver = {
    'major': 0,
    'minor': 0,
    'patch': 0,
    'build': 0,
    'str': "0.0.0.0"
}

baseDir = os.path.dirname(os.path.realpath(__file__))

path_main = baseDir
path_temp = m(baseDir + '/temp')
path_game = m(baseDir + '/games')
path_runtime = m(baseDir + '/runtime')
path_license = f(baseDir + '/LICENSE')
path_updater = f(baseDir + '/updater.py')
path_data = m(baseDir + '/data')
path_assets = m(path_data + "/assets")
path_setting = f(baseDir + '/setting.json')

url_list = 'https://api.mysticrs.tk/list'
url_modpack = 'https://api.mysticrs.tk/modpack'
url_whitelist = 'https://api.mysticrs.tk/whitelist'
url_forgot_password = 'https://account.mojang.com/password'
url_file = 'https://files.mysticrs.tk/'
url_runtime = 'https://files.mysticrs.tk/{os}/'

# i don't know where this field is used.
cn = 'zero'

