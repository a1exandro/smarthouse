from engine import ctrls, hndls
import time,sys,os
from engine import conf

class TSystem:
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

        self.ctrlEng = ctrls.ctrls(self.onControllerMessage)
        self.ctrlEng.loadMods(self.cfg['mod_dir'])

        self.hndlEng = hndls.hndls(self.onHandlerMessage,self.onCommand)
        self.hndlEng.loadMods(self.cfg['hndl_dir'])
        engn = engine(self.hndlEng,self.ctrlEng)
        while (self.runn):
            time.sleep(1)

    def onControllerMessage(self,msg):
        try:
            msg['hId'] = 0

            packetData = msg['msg'].split(';')
            for m in packetData:
                msg['data'] = m.split(' ')
                msg['msg'] = m.strip()
                if len(msg['msg']):
                    self.hndlEng.sendMsg(msg)
        except BaseException as e:
            print (str(e))
    def onHandlerMessage(self,msg):
        try:
            self.ctrlEng.sendMsg(msg)
        except BaseException as e:
            print (str(e))

    def onCommand(self,cmd,args):
        if cmd == 'exit' and args == 1:
            self.close()
        elif cmd == 'reload modules':
            self.ctrlEng.reloadMods()
            self.hndlEng.reloadMods()
            print('All modules has been reloaded')
        elif cmd == 'restart':
            self.close()
            python = sys.executable
            #p = '\"\"'+python+'\"\"'
            #python = r'C:\Program Files (x86)\Python 3.3\python.exe'
            os.execl(python,python, * sys.argv)

    def close(self):
        try:
            self.hndlEng.stopAllThreads()
            self.ctrlEng.stopAllThreads()
            conf.close()
            self.runn = 0
        except BaseException as e:
            print (str(e))


class engine:
    hndlrs = None
    ctrls = None
    def __init__(self,handlers,controllers):
        self.hndlrs = handlers
        self.ctrls = controllers



