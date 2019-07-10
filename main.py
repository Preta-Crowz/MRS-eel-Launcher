import eel, json, os
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
    'data':os.path.normpath(baseDir+'./data/')
  },
  'url':{
    'list':'https://api.mysticrs.tk/list',
    'info':'https://api.mysticrs.tk/modpack'
    'white':'https://api.mysticrs.tk/whitelist'
    'mpass':'https://account.mojang.com/password'
  }
}
print(launcher['path'])
exit()
eel.init('page')
eel.start('wip.html')