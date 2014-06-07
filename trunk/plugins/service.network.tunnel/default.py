# -*- coding: utf-8 -*-

import xbmc, xbmcaddon, xbmcgui, sys, os


sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib'))


__scriptid__ = "service.network.tunnel"
__addon__ = xbmcaddon.Addon(__scriptid__)
__providers__ = ['McIntyreMedia', 'Custom']
    
def authenticateAndWriteDNS():
    providerid     = __addon__.getSetting('provider')
    providername   = __providers__[int(providerid)]
    providermodule = map(__import__, [providername])[0]
    provider       = getattr(providermodule, providername)(__addon__)
    
    try:
        xbmc.log("Authenticating %s" % (providername))
        if provider.authenticate():
            xbmc.log("Writing DNS settings")
            provider.writeDNS()
    except Exception as e:
        dialog = xbmcgui.Dialog()
        errstrings = str(e).split('|')
        dialog.ok("McIntyreMedia.tv Tunnel Error", *errstrings)
        

if __name__ == "__main__":
    enabled = __addon__.getSetting('enabled')
    if enabled == 'true':
        authenticateAndWriteDNS()
      
