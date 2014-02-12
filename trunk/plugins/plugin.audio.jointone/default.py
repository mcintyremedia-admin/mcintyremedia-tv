import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
from xml.dom import minidom


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

baseurl = 'http://www.jointone.com/player'
playlisturl = "%s/xml/player_config.xml" % baseurl
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

        for mix in album.getElementsByTagName('mix'):
	    name = getChildValue(mix, 'name')
	    title = getChildValue(mix, 'title')
	    date = getChildValue(mix, 'date')
	    description = getChildValue(mix, 'description')
	    playlist = getChildValue(mix, 'playlist')

	    url = build_url({'mode': 'mix', 'name': name, 'title': title, 'playlist': playlist, 'path' : path})            
	    li = xbmcgui.ListItem("%s (%s)" % (title, date), iconImage='DefaultAudio.png')	   
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'mix':
	title = args.get('title', [None])[0]
        path = args.get('path', [None])[0]
	name = args.get('name', [None])[0]
	playlist = args.get('playlist', [None])[0]
        audiofolder = getAudioFolder(playlistdom)

	playurl = "%s/%s/%s/%s/%s.mp3" % (baseurl, audiofolder, path, name, name)	
	xbmc.Player().play(playurl)
