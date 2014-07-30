import os
from SettingsException import SettingsException

class EmailSettings(object):
    
    __STANDARDPROVIDERS__ = None
    __CUSTOM_PROVIDER__   = 21    

    def __init__(self, addon, settingsfile):
        self.username = addon.getSetting('username')
        self.password = addon.getSetting('password')
        self.provider = addon.getSetting('provider')
        self.server   = addon.getSetting('server')
        self.port     = addon.getSetting('port')
        self.usessl   = addon.getSetting('usessl')
        self.to       = addon.getSetting('emailto')
   
        if (not self.username): raise SettingsException(40001)
        if (not self.password): raise SettingsException(40002)
        if (not self.provider): raise SettingsException(40003)

        if int(self.provider) != EmailSettings.__CUSTOM_PROVIDER__:
            if EmailSettings.__STANDARDPROVIDERS__ == None:
                EmailSettings.__STANDARDPROVIDERS__ = []
                if not os.path.exists(settingsfile):
                    raise SettingsException(50001)
                else:
                    for line in open(settingsfile):                        
                        EmailSettings.__STANDARDPROVIDERS__.append(line.strip().split(','))
                        
            providerdetails = EmailSettings.__STANDARDPROVIDERS__[int(self.provider)]
          
            self.server   =  providerdetails[1]
            self.port     =  providerdetails[2]
            self.usessl   = (providerdetails[3] == 'Yes')

        if (not self.server): raise SettingsException(40004)
        if (not self.port  ): raise SettingsException(40005)
        #if (not self.usessl): raise SettingsException(40006)
        if (not self.to    ): raise SettingsException(40007)


