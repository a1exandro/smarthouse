__author__ = 'a1ex!'
__version__ = '1.0'

inf = {'version':__version__,'author':__author__}
import base_ctrl
import threading
import time
from engine import conf

import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.mime.application import MIMEApplication

import poplib
import email


class emailer(base_ctrl.baseCtrl):
    cb = None
    runn = 0
    cId = 0
    lastReq = 0

    a_user = conf.get('user','email_controller')
    a_pw = conf.get('pw','email_controller')
    smtp = conf.get('smtp','email_controller')
    pop = conf.get('pop','email_controller')
    admin_email = conf.get('admin_email','email_controller')
    sleep_time = int(conf.get('sleep_time','email_controller'))
    board_id = int(conf.get('board_id'))
    timeout = int(conf.get('timeout','email_controller'))

    def __init__(self,callback,id):
        super().__init__()
        self.cb = callback
        self.cId = id
        self.lastReq = time.time()
        print('EMAIL controller loaded',inf)

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

        self.inpThread = threading.Thread(target=self.keepAlive, args=())
        self.inpThread.start()

        while self.runn:
            it = self.popQueue()
            if it:
                self.send(it)
        print ('Stopping EMAIL controller...')

    def keepAlive(self):
        while self.runn:
            try:
                self.check()
            except BaseException as e:
                print ('email check error: ',str(e))
            time.sleep(self.sleep_time)
        

    def onRecv(self,data):
        args = {'cId':self.cId,'uId':'0','msg':data,'type':'text_cmd'}
        self.cb(base_ctrl.ev_rcv,args)
        print('EMAIL recv: %s'%data)

    def check(self):
        pop = poplib.POP3_SSL(self.pop,timeout=self.timeout)
        pop.user(self.a_user)
        pop.pass_(self.a_pw)
        emails, total_bytes = pop.stat()
        data = ''
        for i in range(emails):
            response = pop.retr(i+1)
            raw_message = response[1]
            msg = email.message_from_bytes(b'\n'.join(raw_message))

            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_type() == 'text/plain':
                    data += part.get_payload(decode=1).decode("utf-8")
            pop.dele(i+1)
        if len(data):
            self.onRecv(data)
        pop.quit()

    def send(self,msg = {}):
        try:
            if not 'files' in msg: msg['files'] = []
            if not 'msg' in msg: msg['msg'] = ''
            if not 'subject' in msg: msg['subject'] = 'smarthouse'

            self.send_mail(msg['subject'],msg['msg'],msg['files'])

        except BaseException as e:
            print (str(e))


    def send_mail(self, subject, text, files=[]):
        try:
            COMMASPACE = ', '
            send_to = [self.admin_email]
            server = self.smtp
            assert type(send_to)==list
            assert type(files)==list

            msg = MIMEMultipart()
            msg['From'] = self.a_user
            msg['To'] = COMMASPACE.join(send_to)
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject

            print('EMAIL send: %s'%text)

            msg.attach(MIMEText(text))

            for f in files:
                part = MIMEApplication(open(f, 'rb').read())
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
                msg.attach(part)

            smtp = smtplib.SMTP_SSL(server,timeout=self.timeout)
            smtp.login(self.a_user,self.a_pw)
            smtp.sendmail(self.a_user, send_to, msg.as_string())
            smtp.close()
        except BaseException as e:
            print (str(e))
