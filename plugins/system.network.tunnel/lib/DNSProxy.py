import mechanize
import cookielib

class DNSProxy(object):

    __RESOLV__ = r"/etc/resolv.conf"

    def __init__(self, proxyip):
        self.proxyip = proxyip
        self.browser = mechanize.Browser()
                
    def initialiseBrowser(self):        
        br = self.browser
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.addheaders = [("User-agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")]  

        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        
    def login(self, username, password):
        self.initialiseBrowser()        

    def writeDNS(self):
	try:
	   f = open(self.__RESOLV__, "w")
	   for addr in self.proxyip:
              f.write("nameserver %s\n" % addr)
	   f.close
	except IOError as err:
           print err
        