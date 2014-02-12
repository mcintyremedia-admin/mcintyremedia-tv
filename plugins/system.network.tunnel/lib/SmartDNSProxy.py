
import re
import BeautifulSoup

class SmartDNSProxy(DNSProxy):

    _DNS_IP_ = ['8.8.8.8', '8.8.4.4']
    _BASE_ADDR_ = r'https://www.smartdnsproxy.com/'

    def __init__(self):
        super(SmartDNSProxy, self).__init__(self._DNS_IP_)

    def login(self, username, password):
        super(SmartDNSProxy, self).login(self)
        self.br.open('%s/Login' % self._BASE_ADDR_)

        # Select the second (index one) form
        self.br.select_form(nr=0)
        self.br.form['__EVENTTARGET'].readonly = False 
        self.br.form['__EVENTTARGET'] = 'ctl00$ContentPlaceHolderMain$btnSignIn'
        self.br.form['ctl00$ContentPlaceHolderMain$txtEmail'] = 'admin@mcintyremedia.tv'
        self.br.form['ctl00$ContentPlaceHolderMain$txtPassword'] = 'p@$$word'

        # Login
        self.br.submit()
        self.br.open('%s/MyAccount' % self._BASE_ADDR_)

        soup = BeautifulSoup.BeautifulSoup( self.br.response().read() )
        ipre = re.compile("Your Active IP : (.*)")
        x = soup.findAll(text=ipre)
        return x != None
        
        #TODO:: ADD THE CODE TO UPDATE THE IP IF THE ADDRESS CHANGES
        
