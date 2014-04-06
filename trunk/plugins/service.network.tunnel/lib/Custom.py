
import xbmc, xbmcaddon
from DNSProxy import DNSProxy

__scriptid__ = "service.network.tunnel"
__addon__ = xbmcaddon.Addon(__scriptid__)


class Custom(DNSProxy):

    def __init__(self):       
        super(Custom, self).__init__([__addon__.getSetting('customsmartipaddress')])

    def login(self, username, password):
        return True
                        

