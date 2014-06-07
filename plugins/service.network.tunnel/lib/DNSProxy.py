# -*- coding: utf-8 -*-

class DNSProxy(object):

    __RESOLV__ = r"/etc/resolv.conf"
    __DNS_IP__ = []
    
    def __init__(self, addon):
        self.addon = addon

    def authenticate(self):
        return False
                        
    def getProxyDetails(self):
        return self.__DNS_IP__
        
    def writeDNS(self):
        try:
           proxydetails = self.getProxyDetails()
           if len(proxydetails) > 0 :
              f = open(self.__RESOLV__, 'w+')
              for addr in proxydetails:
                 f.write("nameserver %s\n" % addr)
              f.close
        except Exception as err:
           print err
        
