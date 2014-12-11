__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
commands = ['system']

import base_hndl
import subprocess
import zipfile
import os.path
try:
    import requests
except:
    print ('could not load requests lib')
from engine import conf

class h_system(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        print('System handler loaded',inf)

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

    def processMsg(self,data):
        try:
            if not data['msg']['type'] == 'text_cmd': return
            cmd = data['msg']['data']
            if len(cmd) < 2: return

            if cmd[1] == 'exit':
                self.cb(base_hndl.ev_cmd,{'msg':'exit'})
            if cmd[1] == 'restart':
                self.cb(base_hndl.ev_cmd,{'msg':'restart'})
            if cmd[1] == 'exec':
                if (len(cmd) < 3): return
                data['msg']['msg'] = '\n'+self.execCmd(cmd[2:])
                self.send(data['msg'])
            if cmd[1] == 'update':
                if len(cmd) < 3: return
                self.update(cmd[2:])
        except BaseException as e:
            print (str(e))

    def send(self,msg):
        msg['msg'] = 'SYSTEM: ' +  msg['msg']
        self.cb(base_hndl.ev_rcv,msg)

    def update(self,cmd):
        a_user = conf.get('user','http_controller')
        a_pw = conf.get('pw','http_controller')
        timeout = int(conf.get('timeout','http_controller'))

        url = " ".join(cmd)

        r = requests.get(url, auth=(a_user,a_pw),timeout = timeout)

        #if (r.code != 200):
        #    return

        fd = open('update.zip','wb')
        fd.write(r.content)
        fd.close()

        zfile = zipfile.ZipFile("update.zip")
        for name in zfile.namelist():
            (dirname, filename) = os.path.split(name)
            if len(dirname):
                if not os.path.exists(dirname):
                    os.mkdir(dirname)
            if (len(filename)):
                fd = open(name,"wb")
                fd.write(zfile.read(name))
                fd.close()
        zfile.close()
        os.remove('update.zip')
        self.cb(base_hndl.ev_cmd,{'msg':'restart'})

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
            return 'Error while executing command: '+str(e)
