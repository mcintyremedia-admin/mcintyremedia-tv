
import xbmc, xbmcaddon, xbmcgui, sys, os

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib'))

__scriptid__ = "service.network.tunnel"
__addon__ = xbmcaddon.Addon(__scriptid__)
__providers__ = ['SmartDNSProxy']
    
def loginAndWriteDNS():
    providerid     = __addon__.getSetting('provider')
    username       = __addon__.getSetting('username')
    password       = __addon__.getSetting('password')
    providername   = __providers__[int(providerid)]
    providermodule = map(__import__, [providername])[0]
    provider       = getattr(providermodule, providername)()
    
    xbmc.log("Logging into %s with username %s" % (providername, username))
    if provider.login(username, password):
        xbmc.log("Writing DNS settings")
        provider.writeDNS()
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok( "%s : login failed" % providerid)
	


if __name__ == "__main__":
    enabled = __addon__.getSetting('enabled')
    if enabled == 'true':
        loginAndWriteDNS()
      
