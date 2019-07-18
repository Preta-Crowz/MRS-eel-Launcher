import os
baseDir = os.path.dirname(os.path.realpath(__file__))
def hashLoop(d):
    base = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
    r = []
    for a in base:
        for b in base:
            r.append(os.path.normpath(d+"/"+a+b))
    return r

dirs = [
    os.path.normpath(baseDir+'/games'),
    os.path.normpath(baseDir+'/runtime'),
    os.path.normpath(baseDir+'/data'),
    os.path.normpath(baseDir+'/lib'),
    os.path.normpath(baseDir+'/versions'),
    os.path.normpath(baseDir+'/assets'),
    os.path.normpath(baseDir+'/assets/basedatas'),
    os.path.normpath(baseDir+'/assets/indexes'),
    os.path.normpath(baseDir+'/assets/objects'),
    os.path.normpath(baseDir+'/assets/skins'),
    os.path.normpath(baseDir+'/assets/virtual'),
    ]
dirs += hashLoop(os.path.normpath(baseDir+'/assets/objects'))
dirs += hashLoop(os.path.normpath(baseDir+'/assets/skins'))
for d in dirs:
    try: os.mkdir(d)
    except: pass