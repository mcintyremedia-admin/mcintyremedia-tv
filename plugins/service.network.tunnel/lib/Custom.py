# -*- coding: utf-8 -*-

from DNSProxy import DNSProxy

class Custom(DNSProxy):

    def __init__(self, addon):       
        super(Custom, self).__init__(addon)

    def getProxyDetails(self):
        return [self.__addon__.getSetting('customsmartipaddress')]

    def authenticate(self):
        return True