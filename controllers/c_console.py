__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
import base_ctrl
import threading

class console(base_ctrl.baseCtrl):
    cb = None
    runn = 0
    cId = 0
    inpThread = None
    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        print('Console controller loaded',inf)

    def onCommand (self,cmd,args):
        if cmd == base_ctrl.cm_runn:
            self.terminate(args)

    def terminate(self,args):
        self.runn = 0
        self.inpThread._stop()
        super().terminate()

    def getInfo(self):
        return inf

    def run(self,args=0):
        self.runn = 1
        self.inpThread = threading.Thread(target=self.recv, args=())
        self.inpThread.start()
        while self.runn:
            it = self.popQueue()
            if it:
                self.send(it)
        print ('Stopping console controller...')

    def recv(self):
        try:
            while self.runn:
                inp = input()
                args = {'cId':self.cId,'uId':'0','msg':inp,'type':'text_cmd'}
                self.cb(base_ctrl.ev_rcv,args)
        except BaseException as e:
            print (str(e))

    def send(self,msg):
        print(msg['msg'])