
#import re
#import httplib
#import socket
#import ssl
#import urllib2
#import BeautifulSoup
from DNSProxy import DNSProxy


class Tunlr(DNSProxy):

    DNS_IP = ['69.197.169.9', '192.95.16.109']
    BASE_ADDR = r'https://gatekeeper.tunlr.net'
    ACCT_ACTIVE = r'Hello, (.*)'
    LOGIN_ADDR = '%s/login' % BASE_ADDR

    def __init__(self):
        super(Tunlr, self).__init__(self.DNS_IP)

    def login(self, username, password):
        super(Tunlr, self).login(username, password)

        #urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))
        #request = urllib2.Request(self.LOGIN_ADDR)
        #urllib2.urlopen(request)
        
        #self.browser.open(self.LOGIN_ADDR)

        # Select the second (index one) form
        #self.browser.select_form(nr=0)
        #self.browser.form['usermail'] = username
        #self.browser.form['password'] = password

        # Login
        #self.browser.submit()
        #self.browser.open('%s/dashboard' % self.BASE_ADDR)

        # Check response for active account
        #soup = BeautifulSoup.BeautifulSoup( self.browser.response().read() )        
        #acctre = re.compile(self.ACCT_ACTIVE)       
        #acct = soup.findAll(text=acctre)
        #loginstatus = (len(acct) > 0)
        
        #return loginstatus
        return True
        
#class HTTPSConnectionV3(httplib.HTTPSConnection):
#    def __init__(self, *args, **kwargs):
#        httplib.HTTPSConnection.__init__(self, *args, **kwargs)
#        
#    def connect(self):
#        sock = socket.create_connection((self.host, self.port), self.timeout)
#        if self._tunnel_host:
#            self.sock = sock
#            self._tunnel()
#        try:
#            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv3)
#        except ssl.SSLError, e:
#            print("Trying SSLv3.")
#            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv2)
#            
#class HTTPSHandlerV3(urllib2.HTTPSHandler):
#    def https_open(self, req):
#        return self.do_open(HTTPSConnectionV3, req)


#Tunlr().login("mcintyremedia", "p@$$word")

