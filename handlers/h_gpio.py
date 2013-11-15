__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
commands = ['gpio']

import base_hndl
#import RPi.GPIO as GPIO

class system(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
    #    GPIO.setmode(GPIO.BCM)
        print('GPIO handler loaded',inf)

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
        if len(cmd) < 3: return
        try:
            if cmd[1] == 'set':
                if len(cmd) < 4: return
                if (cmd[2] == 'mode'):
                    if (cmd[3] == 'board'):             # numbering mode
                        GPIO.setmode(GPIO.BOARD)
                    else:
                        GPIO.setmode(GPIO.BCM)
                    data['msg']['msg'] = cmd[2] + ' ' + cmd[3]
                    self.send(data['msg'])
                else:
                    p = int(cmd[2][1:])
                    if len(cmd) == 5 and cmd[3] == '=': # set pin
                        GPIO.output(p,int(cmd[4]))
                        data['msg']['msg'] = cmd[2] + ' = ' + str(GPIO.input(p))
                        self.send(data['msg'])
                    else:                               # set pin direction
                        if (cmd[3] == 'out'):
                            GPIO.setup(p,GPIO.OUT)
                        else:
                            GPIO.setup(p,GPIO.IN)
                        data['msg']['msg'] = cmd[2]  + ' ' + cmd[3]
                        self.send(data['msg'])

            elif (cmd[1] == 'get'):
                p = int(cmd[2][1:])
                if len(cmd) == 3:
                    data['msg']['msg'] = cmd[2] + ' = ' + str(GPIO.input(p))
                    self.send(data['msg'])
        except BaseException as e:
            data['msg']['msg'] = str(e)
            self.send(data['msg'])

    def send(self,msg):
        msg['msg'] = 'GPIO: ' +  msg['msg']
        self.cb(base_hndl.ev_rcv,msg)

