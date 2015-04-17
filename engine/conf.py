__author__ = 'a1ex!'

from engine import globals
import inspect

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
        if folder not in globals.cfgParser:
            globals.cfgParser[folder] = {}
        globals.cfgParser[folder][name] = val
    except BaseException as e:
        print (str(e))

def setModuleCfg(val):
    s = inspect.stack()
    m_name = inspect.getmodulename(s[1][1])
    set(m_name,val,'configs')
    save()

def getModuleCfg():
    s = inspect.stack()
    m_name = inspect.getmodulename(s[1][1])
    return get(m_name,'configs')

def getModuleStatus():
    s = inspect.stack()
    m_name = inspect.getmodulename(s[1][1])
    return get(m_name,'statuses')

def setModuleStatus(val):
    s = inspect.stack()
    m_name = inspect.getmodulename(s[1][1])
    set(m_name,val,'statuses')
    save()

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
