# -*- coding: utf-8 -*-

import xmlrpclib

from DNSProxy import DNSProxy
    
class UserState:
    Authenticated, Unknown, Active, Expired, IPChangeRequired, AddedNew, Error = range(7)
    
    
class McIntyreMedia(DNSProxy):
    
    __AUTH_SERVICE__ = "http://54.248.247.62:8000/"
    __USER_SETTING__ = 'username'

    def __init__(self, addon):
        super(McIntyreMedia, self).__init__(addon)
        self.authproxy = xmlrpclib.ServerProxy(self.__AUTH_SERVICE__)
       
    def getusername(self):
        return self.addon.getSetting(self.__USER_SETTING__)
    
    def authenticate(self):                
        return self._call(self.authproxy.authenticate)        
        
    def getProxyDetails(self):         
        return self._call(self.authproxy.getProxyDetails)
                        
    def _call(self, fn):
        try:
            return fn(self.getusername())            
        except xmlrpclib.Fault as e:
            if e.faultCode == UserState.Unknown:
                raise Exception(self.addon.getLocalizedString(40001) % e.faultString)
            elif e.faultCode == UserState.Expired:
                raise Exception(self.addon.getLocalizedString(40002))
            elif e.faultCode == UserState.Error:
                raise Exception(e.faultString)
        except Exception as e:
                raise Exception("%s|%s" % (self.addon.getLocalizedString(40003), str(e)))                
