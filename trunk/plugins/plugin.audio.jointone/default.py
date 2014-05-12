import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
from BeautifulSoup import BeautifulSoup


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

jointonebase = 'http://www.jointone.com/'
 
mode = args.get('mode', None)

def build_url(query):
    return base_url + '?' + urllib.urlencode(query) 

if __name__ == "__main__":

    if mode is None:

        jointonesoup = BeautifulSoup(urllib.urlopen(jointonebase))
        for tag in jointonesoup.findAll("div", attrs={"class" : "jplayer-playlist-item"}):
            url = build_url({'mode': 'playlist', 'title': tag['name'], 'img': tag['imgloc'], 'playlistid': tag['val'], 'imgloc' : tag['imgloc']})
            li = xbmcgui.ListItem(tag['name'], iconImage=tag['imgloc'])
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
 
        xbmcplugin.endOfDirectory(addon_handle) 

    elif mode[0] == 'playlist':

        title = args.get('title', [None])[0]
        imgloc = args.get('imgloc', [None])[0]
        playlistid = args.get('playlistid', [None])[0]
        jointonesoup = BeautifulSoup(urllib.urlopen(jointonebase))
        for tag in jointonesoup.findAll("div", attrs={"class" : "jplayer-panel-hidden-wrapper-left-item", "playlist": playlistid}):	      
            title    = tag['title']
            value    = tag['val']
            order    = tag['order']
            playpath = tag['rel']
            date     = tag.find(attrs = {"class" : "jplayer-hidden-track-date"}).text
            url      = build_url({'mode': 'mix', 'value': value, 'title': title, 'playlistid': playlistid, date : 'date', 'playpath' : playpath})            
            li       = xbmcgui.ListItem("%s (%s)" % (title, date), iconImage=imgloc)	   
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'mix':
        title   = args.get('title',    [None])[0]
        path    = args.get('path',     [None])[0]	  
        playurl = args.get('playpath', [None])[0]        

        xbmc.Player().play(playurl)
