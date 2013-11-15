__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
import base_ctrl
import socket
import threading
from engine import conf

class tcp_srv(base_ctrl.baseCtrl):
    cb = None
    runn = 0
    cId = 0
    clients = []

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id

        self.HOST = conf.get('tcp_controller_bind_addr')
        if (not self.HOST): self.HOST = '0.0.0.0'
        self.PORT = conf.get('tcp_controller_bind_port')
        if (not self.PORT): self.PORT = 1352

        print('TCP controller loaded',inf)

    def onCommand (self,cmd,args):
        if cmd == base_ctrl.cm_runn:
            self.terminate(args)

    def terminate(self,args):
        try:
            self.runn = args
            for cl in self.clients:
                cl['conn'].close()
            self.server_socket.close()
            super().terminate()
        except BaseException as e:
            print (str(e))

    def getInfo(self):
        return inf

    def run(self,args=0):
        self.runn = 1
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen(5)

            inpThread = threading.Thread(target=self.recv_conn, args=())
            inpThread.start()
        except BaseException as e:
            self.runn = 0
            print (str(e))

        while self.runn:
            it = self.popQueue()
            if it:
                self.send(it)
        print ('Stopping TCP controller...')

    def recv_conn(self):
        try:
            while self.runn:
                conn,addr = self.server_socket.accept()
                rcvThread = threading.Thread(target=self.recv_data, args=(conn,addr))
                rcvThread.start()
                cl = {'addr':addr,'conn':conn}
                self.clients.append(cl)
        except BaseException as e:
            print (str(e))


    def recv_data(self,conn,addr):
        try:
            while conn:
                data = conn.recv(1024).decode("utf-8")
                if not data: break
                args = {'cId':self.cId,'uId':addr,'msg':data,'type':'text_cmd'}
                self.cb(base_ctrl.ev_rcv,args)
            for cl in self.clients:
                if cl['addr'] == addr:
                    self.clients.remove(cl)
                    conn.close()
                    break
        except BaseException as e:
            print (str(e))

    def send(self,msg):
        try:
            for cl in self.clients:
                if cl['addr'] == msg['id']:
                    cl['conn'].send(bytes(msg['msg'], 'UTF-8'))
        except BaseException as e:
            print (str(e))



