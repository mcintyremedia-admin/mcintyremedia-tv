
import xbmcaddon, xbmcgui, sys, os

sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))

__scriptid__ = "service.network.tunnel"
__addoninfo__ = xbmcaddon.Addon(id)(__scriptid__)
__addon__ = __addoninfo__["addon"]

    
def loginAndWriteDNS():
    providerid     = __addon__.getSetting('provider')
    username       = __addon__.getSetting('username')
    password       = __addon__.getSetting('password')
    providermodule = map(__import__, [providerid])[0]
    provider       = getattr(providermodule, providerid)()
    if provider.login(username, password):
        provider.writeDNS()
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok( "%s : login failed" % [providerid])
	


if __name__ == "__main__":
    firsttimerun = __addon__.getSetting('firsttimerun')
    if firsttimerun == 'true':
    #Show msgbox and addon settings screen
        pass
   
    enabled = __addon__.getSetting('enabled')
    if enabled == 'true':
        loginAndWriteDNS()
      
