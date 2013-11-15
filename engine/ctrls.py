import os
import sys
import importlib
import inspect
import threading
import random
import time
import imp

class ctrls:
    mods = []
    base_mod = None

    hndlCb = None

    def genId(self):
        find = False
        while find == False:
            id = random.randint(1,100000000)
            find = True
            for thread in self.mods:
                if thread['id'] == id:
                    find = False
        return id


    def callBack(self,event,args):
        if event == self.base_mod.ev_rcv:
            self.hndlCb(args)

    def reloadMods(self):
        for m in self.mods:
            imp.reload(m['module'])


    def loadMods(self,mDir):
        sys.path.insert( 0, mDir)
        self.base_mod = importlib.import_module('base_ctrl')
        for files in os.listdir('./%s/'%mDir):
            if files.endswith('.py'):
                mod_name = files[:-3]
                if mod_name != "base_ctrl" and mod_name != "__init__":
                    pkg = importlib.import_module(mod_name)
                    for elem in dir (pkg):
                        obj = getattr (pkg, elem)
                        if inspect.isclass (obj): # Это класс?
                            if issubclass (obj, self.base_mod.baseCtrl): # Класс производный от baseCtrl?
                                nId = self.genId()
                                ct = obj(self.callBack,nId)
                                t = threading.Thread(target=ct.run, args=())

                                self.mods.append({'name':mod_name,'id':nId,'info:':ct.getInfo(),'commands':ct.getCommands(),'obj':ct,'thread':t,'module':pkg})
                                t.daemon = True
                                t.start()
    def stopAllThreads(self):
        print('Terminating all controllers...')
        for thread in self.mods:
            thread['obj'].onCommand(self.base_mod.cm_runn,0)
            thread['thread']._stop()
        time.sleep(1)
        print('Done')

    def sendMsg(self,msg):
        if (str(msg['cId']).isdigit()):
            if msg['cId'] == 0: # msg to everybody
                for thread in self.mods:
                    thread['obj'].sendMsg(msg['uId'],msg['msg'])
            else:
                for thread in self.mods:
                    if thread['id'] == msg['cId']:
                        thread['obj'].sendMsg(msg['uId'],msg['msg'])
                        break
        else:
            for thread in self.mods:
                if thread['name'] == msg['cId']:
                    thread['obj'].sendMsg(msg['uId'],msg['msg'])
                    break

    def getIdByName(self,name):
        for thread in self.mods:
            if thread['name'] == name:
                return thread['id']
        return 0

    def __init__(self,hndlCb):
        self.hndlCb = hndlCb
        print('Initializing controllers...')


