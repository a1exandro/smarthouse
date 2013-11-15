__author__ = 'a1ex!'
from collections import deque
import threading

################################
cm_runn = 0

################################
ev_rcv = 0
ev_cmd = 1

################################
class baseHndl(object):

    def __init__(self):
        self.runn = 1
        self.qLock = threading.Lock()
        self.q = deque()
    def terminate(self):
        if self.qLock.locked():
            self.qLock.release()
        self.runn = 0
    def getInfo(self):
        return {'version': 'unknown','author':__author__}
    def sendMsg(self,msg,args=0):
        if self.runn == 0: return
        self.q.append({'msg':msg.copy(),'args':args})
        if self.qLock.locked():
            self.qLock.release()
    def onCommand(self,cmd,args):
        pass
    def run(self,args=0):
        pass
    def getCommands(self):
        return []
    def popQueue(self):
        if len(self.q) > 0:
            return self.q.popleft()
        else:
            self.qLock.acquire(1)
            return None
