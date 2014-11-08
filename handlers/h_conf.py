__author__ = 'a1ex!'
__version__ = '1.0'



inf = {'version':__version__,'author':__author__}
commands = ['conf']

import base_hndl
from engine import conf
import json

class h_conf(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        print('CONF handler loaded',inf)

    def onCommand (self,cmd,args):
        if cmd == base_hndl.cm_runn:
            self.terminate(args)

    def getCommands(self):
        return commands

    def terminate(self,args):
        self.runn = args
        super().terminate()

    def getInfo(self):
        return inf

    def run(self,args=0):
        self.runn = 1
        while self.runn:
            it = self.popQueue()
            if it:
                self.processMsg(it)

# conf set port = 1352
# conf get port
# conf save

    def processMsg(self,data):
        if not data['msg']['type'] == 'text_cmd': return
        cmd = data['msg']['data']
        if len(cmd) < 2: return
        jdata = {}
        try:
            if (cmd[1] == 'save'):
                conf.save()
            elif cmd[1] == 'set':
                if len(cmd) < 5: return

                jdata['type'] = 'value'
                params = cmd[2].split('/')
                if len(params) == 1:
                    param = params[0]
                    folder='main'
                else:
                    param = params[1]
                    folder= params[0]

                conf.set(param,cmd[4],folder)
                jdata['name'] = cmd[2]
                jdata['data'] = cmd[4]
                data['msg']['msg'] = json.dumps(jdata)
                self.send(data['msg'])


            elif (cmd[1] == 'get'):
                jdata['type'] = 'value'
                if len(cmd) == 3:
                    params = cmd[2].split('/')
                    if len(params) == 1:
                        param = params[0]
                        folder='main'
                    else:
                        param = params[1]
                        folder= params[0]

                    jdata['name'] = cmd[2]
                    jdata['data'] = conf.get(param,folder)
                    data['msg']['msg'] = json.dumps(jdata)
                    self.send(data['msg'])
        except BaseException as e:
            data['msg']['msg'] = str(e)
            self.send(data['msg'])

    def send(self,msg):
        msg['msg'] = 'CONF: ' +  msg['msg']
        self.cb(base_hndl.ev_rcv,msg)

