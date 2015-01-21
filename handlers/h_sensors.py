__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
commands = ['sensors']

import base_hndl
import json
import os
from engine import conf
import re
import time
try:
    import RPi.GPIO as GPIO
except:
    print('RPi.GPIO not found',inf)

class h_sensors(base_hndl.baseHndl):
    cb = None
    runn = 0
    cId = 0
    w1_dev_dir = conf.get('w1_dev_dir','main')
    trackedSens = []

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            time.sleep(2)
            self.onModuleCfgChanged()
            print('SENSORS handler loaded',inf)
        except:
            print('Could not load SENSORS module')

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

    #sensors get a123456
    #sensors get list

    def processMsg(self,data):
        jdata = {}
        if not data['msg']['type'] == 'text_cmd':
            return
        cmd = data['msg']['data']
        if len(cmd) < 3:
            return
        try:
            if (cmd[1] == 'get'):
                if (len(cmd) > 2):
                    if (cmd[2] == 'cfg'):
                        cfg = conf.getModuleCfg()
                        if cfg:
                            jdata['type'] = 'cfg'
                            jdata['data'] = cfg
                            data['msg']['msg'] = json.dumps(jdata)
                            self.send(data['msg'])
                    elif (cmd[2] == 'list'):
                        data['msg']['msg'] = self.getList()
                        self.send(data['msg'])
                    else:
                        data['msg']['msg'] = self.getSensorData(cmd[2])
                        self.send(data['msg'])
            elif (cmd[1] == 'track'):
                self.addTrackedSensor(cmd[2])
            elif (cmd[1] == 'set'):
                if (cmd[2] == 'cfg'):
                    conf.setModuleCfg(' '.join(cmd[3:]))
                    self.onModuleCfgChanged();

        except BaseException as e:
            data['msg']['msg'] = str(e)
            self.send(data['msg'])

    def send(self,msg):
        msg['msg'] = 'SENSORS: ' + msg['msg']
        self.cb(base_hndl.ev_rcv,msg)

    def addTrackedSensor(self, data):
        sensor_data = json.loads(self.getSensorData(data))
        self.trackedSens.append(sensor_data)

    def getSensorData(self, sensor):
        a = (sensor[1:])
        if (sensor[0] == 'T'):
            return self.getTempSens(a)
        elif sensor[0] == 'D':
            return self.getDigitalSens(a)

    def getDigitalSens(self, addr):
        try:
            GPIO.setup(int(addr),GPIO.IN)
            val = GPIO.input(int(addr))
        except:
            val = 0
        data = {'addr':addr, 'data':val}
        data['type'] = 'D'
        return json.dumps(data)

    def getTempSens(self, addr):
        t = 0
        fName = self.w1_dev_dir+'/'+addr+'/w1_slave'
        try:
            f = open(fName)
            if f:
                sensData = f.read()
                f.close()

                temp = re.findall(r't=([0-9]+)', sensData, re.DOTALL)

                if len(temp):
                    t = float(temp[0])/1000
        except:
            t = 0
        data = {'addr':addr,'data':t}
        data['type'] = 'T'
        return json.dumps(data)

    def getList(self):
        data = []
        for dev in os.listdir(self.w1_dev_dir):
            if dev != 'w1_bus_master1':
                data.append(dev)

        res = {"type":"list","data":data}
        return json.dumps(res)

    def getStatusData(self):
        data = []
        i = 0
        for sensor in self.trackedSens:
            s_addr = str(sensor['type']) + str(sensor['addr'])
            s_val = json.loads(self.getSensorData(s_addr))
            if abs(s_val['data'] - sensor['data']) > 0.5:
                data.append(s_val)
                self.trackedSens[i] = s_val
            i += 1
        #print(str(sensor['addr']),s_val,sensor['data'],abs(s_val['data'] - sensor['data']))
        if len(data):
            return 'SENSORS: ' + json.dumps(data)
        else:
            return None

    def onModuleCfgChanged(self):
        cfg = json.loads(conf.getModuleCfg())
        #self.trackedSens.clear()
        del self.trackedSens[:]
        for sens in cfg['sensors']:
            self.addTrackedSensor(sens['type'] + sens['addr'])