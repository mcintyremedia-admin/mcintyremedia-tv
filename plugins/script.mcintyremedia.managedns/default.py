import xbmc
import xbmcaddon
import xbmcgui
import os

__addon__       = xbmcaddon.Addon()
__version__     = __addon__.getAddonInfo('version')
__id__          = __addon__.getAddonInfo('id')
__language__    = __addon__.getLocalizedString
__cwd__         = __addon__.getAddonInfo('path')

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources') )
sys.path.append (BASE_RESOURCE_PATH)
print "[SCRIPT] '%s: version %s' initialized!" % (__id__, __version__, )

if (__name__ == "__main__"):
   xbmc.executebuiltin('Addon.OpenSettings(service.network.tunnel)')
   if xbmcgui.Dialog().yesno("McIntyreMedia Tunnel", __addon__.getLocalizedString(601), __addon__.getLocalizedString(602)):
       xbmc.executebuiltin('XBMC.Reboot()', True)


