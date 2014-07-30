# -*- coding: utf-8 -*-

import xbmc, xbmcaddon, xbmcgui, sys, os

__addon__        = xbmcaddon.Addon("script.mcintyremedia.support")
__cwd__          = __addon__.getAddonInfo('path')
__settingsfile__ = os.path.join(__cwd__, "resources/commonproviders.txt")    

sys.path.append(os.path.join(__cwd__, 'lib'))
sys.path.append(xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' )))


from SupportMailer import SupportMailer
from EmailSettings import EmailSettings
from SettingsException import SettingsException

#from HelpDialog import MainDialog
       
if __name__ == "__main__":                         
    try:                                   
        if xbmcgui.Dialog().yesno(__addon__.getLocalizedString(10001), 
                                  __addon__.getLocalizedString(10002)):
            mailer=SupportMailer(EmailSettings(__addon__, __settingsfile__)) 
            mailer.mailfile("User logfile", "User logfile", 
                            os.path.join(xbmc.translatePath('special://logpath'), 'xbmc.log'))
            
            xbmcgui.Dialog().ok( __addon__.getLocalizedString(10001), __addon__.getLocalizedString(10003) )

    except SettingsException as e:
        xbmcgui.Dialog().ok( __addon__.getLocalizedString(10001), "Error : %s" % __addon__.getLocalizedString(e.value) )
        __addon__.openSettings()
    except Exception as e:
        print str(e)
        xbmcgui.Dialog().ok( __addon__.getLocalizedString(10001), "Unexpected Error : %s" % str(e), __addon__.getLocalizedString(10004) )