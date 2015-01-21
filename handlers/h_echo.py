__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}

import base_hndl
import threading

class h_echo(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0
    enabled = 0

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        print('Echo handler loaded',inf)

    def onCommand (self,cmd,args):
        if cmd == base_hndl.cm_runn:
            self.terminate(args)

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

    def processMsg(self,msg):
        if not msg['msg']['type'] == 'text_cmd': return;
        if msg['msg']['msg'] == 'echo on':
            self.enabled = True
        elif msg['msg']['msg'] == 'echo off':
            self.enabled = False

        if (self.enabled):
            #msg['msg']['msg'] = 'test'
            self.send(msg['msg'])

    def send(self,msg):
        self.cb(base_hndl.ev_rcv,msg)
