import eel, json, os, pypresence, logging, time
import pycraft
log = logging.Logger("MRS")
rpc = pypresence.Presence(490596975457337374)
rpc.connect()

baseDir = os.path.dirname(os.path.realpath(__file__))+'/'
launcher = {
  'name':'MRS Minecraft Launcher',
  'cn':'CODENAME_ZERO',
  'ver':{
    'major':0,
    'minor':0,
    'patch':0,
    'build':0
  },
  'path':{
    'main':baseDir,
    'game':os.path.normpath(baseDir+'./games/'),
    'java':os.path.normpath(baseDir+'./runtime/'),
    'license':os.path.normpath(baseDir+'./LICENSE'),
    'updater':os.path.normpath(baseDir+'./updater.py'),
    'data':os.path.normpath(baseDir+'./data/'),
    'mclib':os.path.normpath(baseDir+'./forge/'),
  },
  'url':{
    'list':'https://api.mysticrs.tk/list',
    'info':'https://api.mysticrs.tk/modpack',
    'white':'https://api.mysticrs.tk/whitelist',
    'mpass':'https://account.mojang.com/password'
  }
}
eel.init('page')
rpc.update(state='Developing',details='MRS NEW LAUNCHER',large_image='favicon',large_text='Nyaa',start=int(time.time()))
eel.start('wip.html')