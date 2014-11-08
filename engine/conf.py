__author__ = 'a1ex!'

from engine import globals

def init(l_cfg):
    try:
        globals.cfgParser.read(globals.cfg['cfg_path'])
        set('version',l_cfg['version'])
    except BaseException as e:
        print (str(e))

def get(name,folder='main'):
    r = ''
    try:
        r = globals.cfgParser.get(folder,name)
    finally:
        return r

def set(name,val,folder='main'):
    try:
        if not folder in globals.cfgParser: globals.cfgParser[folder] = {}
        globals.cfgParser[folder][name] = val
    except BaseException as e:
        print (str(e))


def close():
    try:
        with open(globals.cfg['cfg_path'], 'w') as configfile:
            globals.cfgParser.write(configfile)
    except BaseException as e:
        print (str(e))
    finally:
        print('conf saved')

def save():
    close()