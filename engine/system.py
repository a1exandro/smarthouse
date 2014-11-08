from engine import ctrls, hndls
import time,sys,os
from engine import conf

class System:
    cfg = {}
    runn = 0
    ctrlEng = None
    hndlEng = None
    engn = None

    def __init__(self,cfg):
        self.cfg = cfg
        self.runn = 1
        conf.init(cfg)

    def init(self):
        if not self.runn: return

        self.hndlEng = hndls.hndls(self.onHandlerMessage,self.onHndlCommand)
        self.hndlEng.loadMods(self.cfg['hndl_dir'])
		
        self.ctrlEng = ctrls.ctrls(self.onControllerMessage,self.onCtrlCommand)
        self.ctrlEng.loadMods(self.cfg['mod_dir'])

        self.clearTmp()

        while (self.runn):
            time.sleep(1)

    def onControllerMessage(self,msg):
        try:
            msg['hId'] = 0

            packetData = msg['msg'].split(';')
            for m in packetData:
                m = m.strip()
                msg['msg'] = m
                msg['data'] = m.split(' ')
                if len(msg['msg']):
                    self.hndlEng.sendMsg(msg)
        except BaseException as e:
            print (str(e))

    def onHandlerMessage(self,msg):
        try:
            self.ctrlEng.sendMsg(msg)
        except BaseException as e:
            print (str(e))

    def onCtrlCommand(self,cmd,args):
        try:
            return self.hndlEng.getAliveData()
        except BaseException as e:
            print (str(e))

    def onHndlCommand(self,cmd,args):
        if cmd == 'exit' and args == 1:
            self.close()
        elif cmd == 'reload modules':
            self.ctrlEng.reloadMods()
            self.hndlEng.reloadMods()
            print('All modules has been reloaded')
        elif cmd == 'restart':
            self.close()
            python = sys.executable

            os.execl(python,python, * sys.argv)

    def close(self):
        try:
            self.hndlEng.stopAllThreads()
            self.ctrlEng.stopAllThreads()
            conf.close()
            self.runn = 0
        except BaseException as e:
            print (str(e))

    def clearTmp(self):
        try:
            for files in os.listdir('./tmp'):
                os.remove('./tmp/'+files)
        except BaseException as e:
            print (str(e))


