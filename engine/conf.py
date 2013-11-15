__author__ = 'a1ex!'

import configparser

cfg = configparser.ConfigParser()
s_cfg = {}

def init(l_cfg):
    global s_cfg,cfg
    s_cfg = l_cfg.copy()
    try:
        cfg.read(s_cfg['cfg_path'])
    except BaseException as e:
        print (str(e))

def get(name,folder='main'):
    global cfg
    r = ''
    try:
        r = cfg[folder][name]
    finally:
        return r

def set(name,val,folder='main'):
    global cfg,s_cfg
    try:
        if not folder in cfg: cfg[folder] = {}
        cfg[folder][name] = val
    except BaseException as e:
        print (str(e))


def close():
    global s_cfg,cfg
    try:
        with open(s_cfg['cfg_path'], 'w') as configfile:
            cfg.write(configfile)
    except BaseException as e:
        print (str(e))
    finally:
        print('conf saved')

def save():
    close()