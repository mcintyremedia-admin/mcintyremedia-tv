
import re
import BeautifulSoup
from DNSProxy import DNSProxy

_DNS_IP_ = ['23.21.43.50', '54.229.171.243']
_BASE_ADDR_ = r'https://www.smartdnsproxy.com'
_ACCT_ACTIVE_ = r'Your Account is Active(.*)'
_IP_MISMATCH_ = r'Your Active IP is not matching your current IP(.*)'
    
class SmartDNSProxy(DNSProxy):

    def __init__(self):
        super(SmartDNSProxy, self).__init__(_DNS_IP_)

    def login(self, username, password):
        super(SmartDNSProxy, self).login(username, password)
        self.browser.open('%s/Login' % _BASE_ADDR_)

        # Select the second (index one) form
        self.browser.select_form(nr=0)
        self.browser.form.find_control("__EVENTTARGET").readonly = False 
        self.browser.form['__EVENTTARGET'] = 'ctl00$ContentPlaceHolderMain$btnSignIn'
        self.browser.form['ctl00$ContentPlaceHolderMain$txtEmail'] = username
        self.browser.form['ctl00$ContentPlaceHolderMain$txtPassword'] = password

        # Login
        self.browser.submit()
        self.browser.open('%s/MyAccount' % _BASE_ADDR_)

        # Check response for active account
        soup = BeautifulSoup.BeautifulSoup( self.browser.response().read() )        
        acctre = re.compile(_ACCT_ACTIVE_)       
        acct = soup.findAll(text=acctre)
        loginstatus = (len(acct) > 0)
        
        #Check if IP address needs updating
        ipre = re.compile(_IP_MISMATCH_)
        ipmismatch = soup.findAll(text=ipre)
        if len(ipmismatch) > 0:
            self.updateIP()
                
        return loginstatus
                        
                            
    def updateIP(self):
        self.browser.select_form(nr=0)
        self.browser.form.find_control("__EVENTTARGET").readonly = False 
        self.browser.form['__EVENTTARGET'] = 'ctl00$ContentPlaceHolderMain$linkUpdateIP'
        self.browser.submit()
        

SmartDNSProxy().login("admin@mcintyremedia.tv", "p@$$word")

