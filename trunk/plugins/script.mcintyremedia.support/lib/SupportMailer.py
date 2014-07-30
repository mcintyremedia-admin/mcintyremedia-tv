import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

class SupportMailer(object):
       
    mail_to = "support@mcintyremedia.tv"
    
    def __init__(self, usersettings):     
        self.usersettings = usersettings
          
    def mail(self, subject, text, attach = None):   
        msg = MIMEMultipart()
        msg['From'] = self.usersettings.username  
        msg['To'] = self.usersettings.to   
        msg['Subject'] = subject   
        msg.attach(MIMEText(text))   
        
        if not attach is None:
            part = MIMEBase('application', 'octet-stream')   
            part.set_payload(open(attach, 'rb').read())   
            Encoders.encode_base64(part)   
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))   
            msg.attach(part)   
            
        print "connecting to %s:%s" % (self.usersettings.server, self.usersettings.port)            
        try:
            mailServer = smtplib.SMTP(self.usersettings.server, int(self.usersettings.port))   
            mailServer.set_debuglevel(1)         
            mailServer.ehlo()   
            mailServer.starttls()   
            mailServer.ehlo()   
            mailServer.login(self.usersettings.username, self.usersettings.password)   
            mailServer.sendmail(self.usersettings.username, self.usersettings.to, msg.as_string())           
            mailServer.close()
        except:
            raise Exception("Mail failure - please check settings")
        
    def mailfile(self, subject, text, filetosend):
        self.mail(subject, text, filetosend)
    
    def mailmessage(self, message):   
        subject = "Request for help"
        self.mail(self.mail_to, subject, message)
    