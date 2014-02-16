import sys
import urllib
import urlparse
import re
import xbmc
import xbmcgui
import xbmcplugin
from xml.dom import minidom


class Mix(object):
    def __init__(self, name, title, date, description, playlist):
       self.name = name
       self.title = title
       self.date = date
       self.description = description
       self.playlist = playlist
       
       titleparts = re.split('\s+#(\d+)',title)
       self.shorttitle = titleparts[0]
       self.titlenumber = 1
       if len(titleparts) > 1:
           self.titlenumber = int(titleparts[1])
           
       
    def xbmcurl(self, xbmcbase):
       return xbmcbase + '?' + urllib.urlencode({'mode': 'mix', 
                                                 'name': self.name, 
                                                 'title': self.title, 
                                                 'playlist': self.playlist, 
                                                 'path' : self.path}) 
                                                 


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

playurl = 'http://www.jointone.com/player'
playlisturl = "%s/xml/player_config.xml" % playurl
playlistdom = minidom.parse(urllib.urlopen(playlisturl))
allalbums = {}

for album in playlistdom.getElementsByTagName("album"):
    allalbums[album.getAttribute('title')] = album


xbmcplugin.setContent(addon_handle, 'audio')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)
 
mode = args.get('mode', None)
 

def getAudioFolder(node):
    return node.getElementsByTagName('settings')[0].getAttribute('audio_folder')

def getChildValue(node, subnode):
    child = node.getElementsByTagName(subnode)[0].firstChild
    if child is None:
        return ""
    else:
        return child.nodeValue 

def getAlbumMixes(album):
    mixes=[]
    for mixnode in album.getElementsByTagName('mix'):
        mixes.append(Mix(getChildValue(mixnode, 'name'),
                         getChildValue(mixnode, 'title'),
                         getChildValue(mixnode, 'date'),
                         getChildValue(mixnode, 'description'),
                         getChildValue(mixnode, 'playlist')))
    return mixes

def getMixNames(album):
    mixnames=[]
    for mixnode in album.getElementsByTagName('mix'):
        mix = Mix(getChildValue(mixnode, 'name'),
                  getChildValue(mixnode, 'title'),
                  getChildValue(mixnode, 'date'),
                  getChildValue(mixnode, 'description'),
                  getChildValue(mixnode, 'playlist'))
        if not mix.shorttitle in mixnames:
            mixnames.append(mix.shorttitle)
    return sorted(mixnames)


if __name__ == "__main__":

    if mode is None:

        for album in playlistdom.getElementsByTagName("album"):
            url = build_url({'mode': 'album', 'title': album.getAttribute('title'), 'path': album.getAttribute('path')})
            li = xbmcgui.ListItem(album.getAttribute('title'), iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
 
        xbmcplugin.endOfDirectory(addon_handle) 

    elif mode[0] == 'album':

        title = args.get('title', [None])[0]
        path = args.get('path', [None])[0]
        album = allalbums[title]        

        for name in getMixNames(album):
            url = build_url({'mode': 'mixcollection', 'name': name, 'title':title, 'path':path})            
            li = xbmcgui.ListItem("%s" % name, iconImage='DefaultAudio.png')	   
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'mixcollection':
        title = args.get('title', [None])[0]
        name = args.get('name', [None])[0]
        path = args.get('path', [None])[0]
        album = allalbums[title]
        albummixes = []        

        for mix in getAlbumMixes(album):
           if mix.shorttitle == name:
                albummixes.append(mix)        
        
        for mix in albummixes:
            url = build_url({'mode': 'mix', 'name': mix.name, 'title':mix.title, 'id':mix.titlenumber, 'path':path}) 
            li = xbmcgui.ListItem("%s (%s)" % (mix.title, mix.date), iconImage='DefaultAudio.png')	   
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'mix':
        title = args.get('title', [None])[0]
        path = args.get('path', [None])[0]
        name = args.get('name', [None])[0]
        playlist = args.get('playlist', [None])[0]
        audiofolder = getAudioFolder(playlistdom)

        playurl = "%s/%s/%s/%s/%s.mp3" % (playurl, audiofolder, path, name, name)	
        xbmc.Player().play(playurl)
