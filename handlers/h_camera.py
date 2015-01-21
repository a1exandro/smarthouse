__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
commands = ['camera']

import base_hndl
import json
import subprocess
from engine import conf
import time

class h_camera(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0

    board_id = int(conf.get('board_id'))

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id

        print('CAMERA handler loaded',inf)

    def onCommand (self,cmd,args):
        if cmd == base_hndl.cm_runn:
            self.terminate(args)

    def getCommands(self):
        return commands

    def terminate(self,args):
        self.runn = 0
        super().terminate()

    def getInfo(self):
        return inf

    def run(self,args=0):
        self.runn = 1
        while self.runn:
            it = self.popQueue()
            if it:
                self.processMsg(it)

    #camera get c0 640x480
    #camera get c0
    def processMsg(self,data):
        if not data['msg']['type'] == 'text_cmd': return
        cmd = data['msg']['data']
        jdata = {}
        if len(cmd) < 3: return
        try:
            if cmd[1] == 'set':
                if (cmd[2] == 'cfg'):
                    conf.setModuleCfg(' '.join(cmd[3:]))
            elif (cmd[1] == 'get'):
                if (cmd[2] == 'cfg'):
                    cfg = conf.getModuleCfg()
                    if cfg:
                        jdata['type'] = 'cfg'
                        jdata['data'] = cfg
                        data['msg']['msg'] = json.dumps(jdata)
                        self.send(data['msg'])
                else:
                    p = int(cmd[2][1:])
                    jdata['type'] = 'picture'
                    jdata['addr'] = p
                    if len(cmd) >= 3:
                        #jdata['data'] = GPIO.input(p)
                        resolution = '640x480'
                        if len(cmd) == 4: resolution = cmd[3]
                        data['msg']['args'] = {}
                        data['msg']['args']['files'] = self.getPicture(p,resolution)
                        jdata['resolution'] = resolution
                        jdata['fname'] = data['msg']['args']['files']
                        data['msg']['msg'] = json.dumps(jdata)
                        self.send(data['msg'])
        except BaseException as e:
            data['msg']['msg'] = str(e)
            self.send(data['msg'])

    def getPicture(self,port,resolution):
        res = []
        try:
            tm = time.time()
            fname = './tmp/came-%s-%s-%s-%d.jpg'%(port,self.board_id,resolution,tm)
            cmd = 'fswebcam --save %s -r %s'%(fname,resolution)

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            if len(err):
                print(err.decode("utf-8"))
            else:
                print(out.decode("utf-8"))
            res.append(fname)
        except BaseException as e:
            print(e)
        return res

    def send(self,msg):
        msg['msg'] = 'CAMERA: ' +  msg['msg']
        self.cb(base_hndl.ev_rcv,msg)

