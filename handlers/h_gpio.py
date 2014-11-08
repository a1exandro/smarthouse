__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
commands = ['gpio']

import base_hndl
import json
try:
    import RPi.GPIO as GPIO
except:
    print('RPi.GPIO not found',inf)

class h_gpio(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        try:
            GPIO.setmode(GPIO.BCM)
            print('GPIO handler loaded',inf)
        except:
            print('Could not load GPIO module',inf)

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

    #gpio set p1 out
    #gpio set p1 = 1
    #gpio get p1
    #gpio set mode board

    def processMsg(self,data):
        if not data['msg']['type'] == 'text_cmd': return
        cmd = data['msg']['data']
        jdata = {}
        if len(cmd) < 3: return
        try:
            if cmd[1] == 'set':
                if len(cmd) < 4: return
                if (cmd[2] == 'mode'):
                    jdata['type'] = 'mode'
                    if (cmd[3] == 'board'):             # numbering mode
                        GPIO.setmode(GPIO.BOARD)
                        jdata['data'] = 'board'
                    else:
                        GPIO.setmode(GPIO.BCM)
                        jdata['data'] = 'bcm'
                    data['msg']['msg'] = json.dumps(jdata)
                    self.send(data['msg'])
                else:
                    p = int(cmd[2][1:])
                    jdata['type'] = 'port_val'
                    jdata['port'] = p
                    if len(cmd) == 5 and cmd[3] == '=': # set pin
                        GPIO.output(p,int(cmd[4]))
                        jdata['data'] = GPIO.input(p)
                        data['msg']['msg'] = json.dumps(jdata)
                        self.send(data['msg'])
                    else:                               # set pin direction
                        jdata['type'] = 'direction'
                        jdata['data'] = cmd[3]
                        if (cmd[3] == 'out'):
                            GPIO.setup(p,GPIO.OUT)
                        else:
                            GPIO.setup(p,GPIO.IN)
                        data['msg']['msg'] = json.dumps(jdata)
                        self.send(data['msg'])

            elif (cmd[1] == 'get'):
                p = int(cmd[2][1:])
                jdata['type'] = 'port_val'
                jdata['port'] = p
                if len(cmd) == 3:
                    jdata['data'] = GPIO.input(p)
                    data['msg']['msg'] = json.dumps(jdata)
                    self.send(data['msg'])
        except BaseException as e:
            data['msg']['msg'] = str(e)
            self.send(data['msg'])

    def send(self,msg):
        msg['msg'] = 'GPIO: ' +  msg['msg']
        self.cb(base_hndl.ev_rcv,msg)

