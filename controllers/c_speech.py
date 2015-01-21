__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
import base_ctrl
import threading
import subprocess
from engine import conf
from engine import mind
try:
    import requests
except:
    print('could not load requests lib')
import json


class speech(base_ctrl.baseCtrl):
    cb = None
    runn = 0
    cId = 0
    inpThread = None
    sox_cmd  = conf.get('sox','speech_controller')
    mplayer_cmd = conf.get('mplayer','speech_controller')
    speech_file = conf.get('speech_file','speech_controller')
    voice_file = conf.get('voice_file','speech_controller')
    http_timeout = int(conf.get('http_timeout','speech_controller'))
    googleSpeechUrl = conf.get('googleSpeechUrl','speech_controller')
    googleVoiceUrl = conf.get('googleVoiceUrl','speech_controller')


    rate =  int(conf.get('rec_rate','speech_controller'))

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        print('Speech controller loaded',inf)

    def onCommand(self,cmd,args):
        if cmd == base_ctrl.cm_runn:
            self.terminate(args)

    def terminate(self,args):
        self.runn = 0
        self.inpThread._stop()
        super().terminate()

    def getInfo(self):
        return inf

    def run(self,args=0):
        self.runn = 0
        self.inpThread = threading.Thread(target=self.recv, args=())
        self.inpThread.start()
        while self.runn:
            it = self.popQueue()
            if it:
                self.send(it)
        print ('Stopping speech controller...')

    def recv(self):
        try:
            while self.runn:
                txt = self.execCmd(self.sox_cmd.split(' '))
                r = requests.post(self.googleSpeechUrl,  headers={'Content-Type':'audio/x-flac; rate=%d'%self.rate} , files={'file':open(self.speech_file,'rb')}, timeout = self.http_timeout)
                if (r.status_code == 200):
                    if (len(r.text)):
                        js = json.loads(r.text)
                        if js['status'] == 0:
                            txt = js['hypotheses'][0]['utterance']
                            cmd = mind.speech2command(txt)
                            args = {'cId':self.cId,'uId':'0','msg':cmd,'type':'text_cmd'}
                            self.cb(base_ctrl.ev_rcv,args)
        except BaseException as e:
            print (str(e))
            self.runn = False

    def send(self,msg):
        cmd = mind.command2speech(msg['msg'])
        url = self.googleVoiceUrl + cmd
        r = requests.get(url, timeout = self.http_timeout)
        if (r.status_code == 200):
            fd = open(self.voice_file,'wb')
            fd.write(r.content)
            fd.close()
            t = self.execCmd( str(self.mplayer_cmd + ' ' + self.voice_file).split(' ') )

    def execCmd(self,cmd):
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = p.communicate()
            if len(err):
                return err.decode("utf-8")
            else:
                return out.decode("utf-8")
        except BaseException as e:
            print (str(e))
            return '0'

