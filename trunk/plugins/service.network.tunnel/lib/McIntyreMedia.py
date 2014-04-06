
from DNSProxy import DNSProxy

_DNS_IP_ = ['192.241.203.97']
    
class McIntyreMedia(DNSProxy):

    def __init__(self):
        super(McIntyreMedia, self).__init__(_DNS_IP_)

    def login(self, username, password):
        return True
                        

