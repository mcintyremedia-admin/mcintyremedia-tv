import urllib,urllib2,re,sys,socket,os,md5,datetime,xbmcplugin,xbmcgui, xbmcaddon

# external libs
sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))
import utils, httplib2, socks, httplib, logging, time
import urllib2

from BeautifulSoup import BeautifulSoup

if xbmcaddon.Addon("service.network.tunnel").getSetting('enabled') != 'true':
    dialog = xbmcgui.Dialog()	
    dialog.ok("Plugin Error", "The McIntyreMedia.tv Tunnel or equivalent service is", "required for this plugin") 
    sys.exit(0)

# setup cache dir
__scriptname__  = 'ITV'
__scriptid__ = "plugin.video.itv"
__addoninfo__ = utils.get_addoninfo(__scriptid__)
__addon__ = __addoninfo__["addon"]
__settings__   = xbmcaddon.Addon(id=__scriptid__)

DIR_USERDATA   = xbmc.translatePath(__addoninfo__["profile"])
SUBTITLES_DIR  = os.path.join(DIR_USERDATA, 'Subtitles')
IMAGE_DIR      = os.path.join(DIR_USERDATA, 'Images')

if not os.path.isdir(DIR_USERDATA):
    os.makedirs(DIR_USERDATA)
if not os.path.isdir(SUBTITLES_DIR):
    os.makedirs(SUBTITLES_DIR)
if not os.path.isdir(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

DEFAULT_PROXY='88.80.190.167'
DEFAULT_PROXY_PORT=80
USE_DEFAULT_PROXY = __settings__.getSetting('proxy_use') != 'true'

def get_proxy():
    proxy_server = None
    proxy_type_id = 0
    proxy_port = 8080
    proxy_user = None
    proxy_pass = None
    try:    
        proxy_server  = __settings__.getSetting('proxy_server') or DEFAULT_PROXY    
        proxy_port    = DEFAULT_PROXY_PORT if (__settings__.getSetting('proxy_port') == '') else int(__settings__.getSetting('proxy_port'))
        proxy_type_id = __settings__.getSetting('proxy_type')
        proxy_user    = __settings__.getSetting('proxy_user')
        proxy_pass    = __settings__.getSetting('proxy_pass')
        
    except:
        pass

    if   proxy_type_id == '0': proxy_type = socks.PROXY_TYPE_HTTP_NO_TUNNEL
    elif proxy_type_id == '1': proxy_type = socks.PROXY_TYPE_HTTP
    elif proxy_type_id == '2': proxy_type = socks.PROXY_TYPE_SOCKS4
    elif proxy_type_id == '3': proxy_type = socks.PROXY_TYPE_SOCKS5

    proxy_dns = True
    
    return (proxy_type, proxy_server, proxy_port, proxy_dns, proxy_user, proxy_pass)

def get_httplib():
    http = None
    try:
        if (__settings__.getSetting('proxy_use') == 'true') or USE_DEFAULT_PROXY:
            (proxy_type, proxy_server, proxy_port, proxy_dns, proxy_user, proxy_pass) = get_proxy()
            logging.info("Using proxy: type %i rdns: %i server: %s port: %s user: %s pass: %s", proxy_type, proxy_dns, proxy_server, proxy_port, "***", "***")
            http = httplib2.Http(proxy_info = httplib2.ProxyInfo(proxy_type, proxy_server, proxy_port, proxy_dns, proxy_user, proxy_pass))
        else:
          logging.info("No Proxy\n")
          http = httplib2.Http()
    except:
        raise
        logging.error('Failed to initialize httplib2 module')

    return http

http = get_httplib()


       
# what OS?        
environment = os.environ.get( "OS", "xbox" )


############## SUBS #################

def chomps(s):
    return s.rstrip('\n')

def httpget(url):
    resp = ''
    data = ''
    http = get_httplib()
    resp, data = http.request(url, "GET")
    return data
    
    
def download_subtitles(url, offset):

    logging.info('subtitles at =%s' % url)
    outfile = os.path.join(SUBTITLES_DIR, 'itv.srt')
    fw = open(outfile, 'w')
    
    if not url:
        fw.write("1\n0:00:00,001 --> 0:01:00,001\nNo subtitles available\n\n")
        fw.close() 
        return outfile
    txt = httpget(url)
    try:
        txt = txt.decode("utf-16")
    except UnicodeDecodeError:
        txt = txt[:-1].decode("utf-16")
    txt = txt.encode('latin-1')
    txt = re.sub("<br/>"," ",txt)
    #print "SUBS %s" % txt
    p= re.compile('^\s*<p.*?begin=\"(.*?)\.([0-9]+)\"\s+.*?end=\"(.*?)\.([0-9]+)\"\s*>(.*?)</p>')
    i=0
    prev = None

    entry = None
    for line in txt.splitlines():
        subtitles1 = re.findall('<p.*?begin="(...........)" end="(...........)".*?">(.*?)</p>',line)
        if subtitles1:
            for start_time, end_time, text in subtitles1:
                r = re.compile('<[^>]*>')
                text = r.sub('',text)
                start_hours = re.findall('(..):..:..:..',start_time)
                start_mins = re.findall('..:(..):..:..', start_time)
                start_secs = re.findall('..:..:(..):..', start_time)
                start_msecs = re.findall('..:..:..:(..)',start_time)
#               start_mil = start_msecs +'0'
                end_hours = re.findall('(..):..:..:..',end_time)
                end_mins = re.findall('..:(..):..:..', end_time)
                end_secs = re.findall('..:..:(..):..', end_time)
                end_msecs = re.findall('..:..:..:(..)',end_time)
#               end_mil = end_msecs +'0'
                entry = "%d\n%s:%s:%s,%s --> %s:%s:%s,%s\n%s\n\n" % (i, start_hours[0], start_mins[0], start_secs[0], start_msecs[0], end_hours[0], end_mins[0], end_secs[0], end_msecs[0], text)
                i=i+1
                #print "ENTRY" + entry
        if entry: 
            fw.write(entry)
    
    fw.close()    
    return outfile

def CATS():
        SHOWS('http://www.itv.com/_data/xml/CatchUpData/CatchUp360/CatchUpMenu.xml')
        #SHOWS('https://www.itv.com/itvplayer/a-z')

def STREAMS():
        streams=[]
        key = get_url('http://www.itv.com/_app/dynamic/AsxHandler.ashx?getkey=please')
        for channel in range(1,5):
                streaminfo = get_url('http://www.itv.com/_app/dynamic/AsxHandler.ashx?key='+key+'&simid=sim'+str(channel)+'&itvsite=ITV&itvarea=SIMULCAST.SIM'+str(channel)+'&pageid=4567756521')
                stream=re.compile('<TITLE>(.+?)</TITLE><REF href="(.+?)" />').findall(streaminfo)
                streams.append(stream[1])
        for name,url in streams:
                addLink(name,url)

def BESTOF(url):
        response = get_url(url).replace('&amp;','&')
        match=re.compile('<li><a href="(.+?)"><img src=".+?" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>').findall(response)
        for url,name in match:
                addDir(name,url,5,'')
                
def BESTOFEPS(url):
        response = get_url(url).replace('&amp;','&')
        eps=re.compile('<a [^>]*?title="Play" href=".+?vodcrid=crid://itv.com/(.+?)&DF=0"><img\s* src="(.*?)" alt="(.*?)"').findall(response)
        if eps:
            for url,thumb,name in eps:
                addDir(name,url,3,'http://itv.com/'+thumb,isFolder=False)
            return
        eps=re.compile('<a [^>]*?title="Play" href=".+?vodcrid=crid://itv.com/(.+?)&DF=0">(.+?)</a>').findall(response)
        if not eps: eps=re.compile('href=".+?vodcrid=crid://itv.com/(.+?)&G=.+?&DF=0">(.+?)</a>').findall(response)
        if not eps:
                eps=re.compile('<meta name="videoVodCrid" content="crid://itv.com/(.+?)">').findall(response)
                name=re.compile('<meta name="videoMetadata" content="(.+?)">').findall(response)
                eps=[(eps[0],name[0])]
        for url,name in eps:
                addDir(name,url,3,'',isFolder=False)
        
def SHOWS(url):
    if __settings__.getSetting('proxy_use') == 'true':
        proxy_server = None
        proxy_type_id = 0
        proxy_port = 8080
        proxy_user = None
        proxy_pass = None
        try:
            proxy_server = __settings__.getSetting('proxy_server')
            proxy_type_id = __settings__.getSetting('proxy_type')
            proxy_port = __settings__.getSetting('proxy_port')
            proxy_user = __settings__.getSetting('proxy_user')
            proxy_pass = __settings__.getSetting('proxy_pass')
        except:
            pass
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        proxy_details = 'http://' + proxy_server + ':' + proxy_port
        passmgr.add_password(None, proxy_details, proxy_user, proxy_pass) 
        authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
        proxy_support = urllib2.ProxyHandler({"http" : proxy_details})

        opener = urllib2.build_opener(proxy_support, authinfo)
        urllib2.install_opener(opener)
    f = urllib2.urlopen('https://www.itv.com/itvplayer/a-z')
    buf = f.read()
    buf=re.sub('&amp;','&',buf)
    buf=re.sub('&middot;','',buf)
    #print "BUF %s" % buf
    f.close()
    match1 = re.findall(ur'<li.*?<div class="tooltip-header">.*?<a href="(.*?)">(.*?)</a>(.*?)</div>(.*?)</div>.*?</li>', buf, flags=re.DOTALL)

    for linkurl, name, rest, rest2 in match1:
    
        match2 = re.findall(ur'<span class="episode-free">(.*?)</span>',rest)
        if match2:
            match3 = re.findall(ur'<img typeof="foaf:Image" src="(.*?)"',rest2, flags=re.DOTALL)
            if match3:
                image = match3[0]
                print image
                image = image.replace('player_image_thumb_standard','posterframe')
            else:
                image = os.path.join(os.getcwd(), 'icon.png')
            name = re.sub('&#039;','\'',name)
            addDir(name+' - '+match2[0],linkurl,2,image)


def EPS(url):
    if __settings__.getSetting('proxy_use') == 'true':
        proxy_server = None
        proxy_type_id = 0
        proxy_port = 8080
        proxy_user = None
        proxy_pass = None
        try:
            proxy_server = __settings__.getSetting('proxy_server')
            proxy_type_id = __settings__.getSetting('proxy_type')
            proxy_port = __settings__.getSetting('proxy_port')
            proxy_user = __settings__.getSetting('proxy_user')
            proxy_pass = __settings__.getSetting('proxy_pass')
        except:
            pass
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        proxy_details = 'http://' + proxy_server + ':' + proxy_port
        passmgr.add_password(None, proxy_details, proxy_user, proxy_pass) 
        authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
        proxy_support = urllib2.ProxyHandler({"http" : proxy_details})

        opener = urllib2.build_opener(proxy_support, authinfo)
        urllib2.install_opener(opener)
    #url = 'https://www.itv.com/itvplayer%s' % url
    url = 'https://www.itv.com%s' % url
    print "URL %s" % url
    f = urllib2.urlopen(url)
    buf = f.read()
    buf=re.sub('&amp;','&',buf)
    buf=re.sub('&middot;','',buf)
    buf=re.sub('&#039;','\'',buf)
    f.close()
    try:
        match_name = re.findall(ur'<h2 class="title episode-title">(.*?)</h2>',buf, flags=re.DOTALL)
        if match_name:
            name2 = match_name[0]
            name3 = match_name[0]
    except:
        pass
        name2 = ""
        name3 = ""
    match1 = re.findall(ur'<div class="views-row.*?<img typeof="foaf:Image" src="(.*?)".*?title="(.*?)" /></a></div></div></div>.*?<a href="(.*?)".*?datatype="xsd:dateTime" content="(.*?)T.*?">.*?</span></div></div></div>(.*?)<div class="field field-name-field-short-synopsis.*?<div class="field-item even">(.*?)</div></div></div>', buf, flags=re.DOTALL)
    if match1:
        print 'BLOODY MATCH !!!!!'
        xbmc.executebuiltin('Container.SetViewMode(504)')
        for image, name,link, date, rest, synopsis in match1:
            print link
            match_series = re.findall(ur'<div class="field-season-number">.*?<div class="field-item even">(.*?)</div>',rest, flags=re.DOTALL)
            if match_series:
                #print "SERIES %s" % match_series[0]
                name2 = name3 + ": Series " + match_series[0]
            match_episode = re.findall(ur'<div class="field-episode-number">.*?<div class="field-item even">(.*?)</div>',rest, flags=re.DOTALL)
            espisode = "1"
            if match_episode:
                #print "EPISODE %s" % match_episode[0]
                episode = match_episode[0]
            addDir2(name2 + ' - ' + name,link,3,date, episode,image.replace('player_image_thumb_standard','posterframe'),synopsis,isFolder=False)
    else:
        print 'TRYING !!!!!'
        match1 = re.findall(ur'about="(.*?)" typeof="sioc:Item foaf:Document">.*?<div class="hero">.*?<h1 class="title episode-title" property="dc:title" datatype="">(.*?) <.*?datatype="xsd:dateTime" content="(.*?)T.*?">.*?</span></div></div></div>(.*?)<div class="field field-name-field-short-synopsis.*?<div class="field-item even">(.*?)</div></div></div>', buf, flags=re.DOTALL)
        if match1:
            for link, name, date, rest, synopsis in match1:
                name = name.strip()
                match_series = re.findall(ur'<div class="field-season-number">.*?<div class="field-item even">(.*?)</div>',rest, flags=re.DOTALL)
                if match_series:
                    print "SERIES %s" % match_series[0]
                    name2 = name3 + ": Series " + match_series[0]
                match_episode = re.findall(ur'<div class="field-episode-number">.*?<div class="field-item even">(.*?)</div>',rest, flags=re.DOTALL)
                espisode = "1"
                if match_episode:
                    print "EPISODE %s" % match_episode[0]
                    episode = match_episode[0]
                image = os.path.join(os.getcwd(), 'icon.png') 
                addDir2(name2 + ' - ' + name,link,3,date, episode,image.replace('player_image_thumb_standard','posterframe'),synopsis,isFolder=False)
        else:
                if re.search('Free Taster',buf):
                    match1 = re.compile('Free Taster      </div>\n.+?class="button button-style-b button-slim"><a href="(.+?)">').findall(buf)
                    print 'EXCEPT !!!!!'
                    url = match1[0]
                    image = os.path.join(os.getcwd(), 'icon.png') 
                    addDir2('Free Taster',url,3,'', '',image,'',isFolder=False)
                    xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
                else:
                    match1 = re.compile('content="(.+?)" />\n.+?meta property="og:url" content="https://www.itv.com/itvplayer/(.+?)" />').findall(buf)
                    print 'EXCEPT !!!!!'
                    image = match1[0][0]
                    url = '/itvplayer/'+match1[0][1]
                    name = url.replace('/itvplayer/',' ').replace('-',' ').upper()
                    addDir2(name,url,3,'', '',image.replace('player_image_thumb_standard','posterframe'),'',isFolder=False)
    xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')


def VIDEO(url):
    if __settings__.getSetting('proxy_use') == 'true':
        proxy_server = None
        proxy_type_id = 0
        proxy_port = 8080
        proxy_user = None
        proxy_pass = None
        try:
            proxy_server = __settings__.getSetting('proxy_server')
            proxy_type_id = __settings__.getSetting('proxy_type')
            proxy_port = __settings__.getSetting('proxy_port')
            proxy_user = __settings__.getSetting('proxy_user')
            proxy_pass = __settings__.getSetting('proxy_pass')
        except:
            pass
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        proxy_details = 'http://' + proxy_server + ':' + proxy_port
        passmgr.add_password(None, proxy_details, proxy_user, proxy_pass) 
        authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
        proxy_support = urllib2.ProxyHandler({"http" : proxy_details})

        opener = urllib2.build_opener(proxy_support, authinfo)
        urllib2.install_opener(opener)
    xbmc.executebuiltin('Container.SetViewMode(504)')
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('ITV Stream', 'Loading stream info')
    #print "URL: " + url
    #url = 'https://www.itv.com/itvplayer' + url
    url = 'https://www.itv.com' + url
    print'=============================================================== '+url
    f = urllib2.urlopen(url)
    buf = f.read()
    buf=re.sub('&#039;','\'',buf)
    f.close()
    if re.search('"title":"This episode is no longer available."',buf):
        dialog = xbmcgui.Dialog()
        dialog.ok("ITV Player", "Sorry This episode is no longer available", "")
    else:
        #print "BUF %s" % buf
        #match1 = re.findall(ur',"productionId":"(.*?)",', buf, flags=re.DOTALL)
        match1 = re.findall(ur'"productionId":"(.*?)",', buf, flags=re.DOTALL)
        if match1:
            productionID = match1[0]
            productionID=re.sub('\\\\','',productionID)
        else:
            print "NO PRODUCTION ID "
        print "Produciton ID is %s" % productionID
        
        #pDialog = xbmcgui.DialogProgress()
        #pDialog.create('ITV Stream', 'Loading stream info')
        #pid = url
        SM_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:itv="http://schemas.datacontract.org/2004/07/Itv.BB.Mercury.Common.Types" xmlns:com="http://schemas.itv.com/2009/05/Common">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:GetPlaylist>
              <tem:request>
            <itv:ProductionId>%s</itv:ProductionId>
            <itv:RequestGuid>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</itv:RequestGuid>
            <itv:Vodcrid>
              <com:Id/>
              <com:Partition>itv.com</com:Partition>
            </itv:Vodcrid>
              </tem:request>
              <tem:userInfo>
            <itv:Broadcaster>Itv</itv:Broadcaster>
            <itv:GeoLocationToken>
              <itv:Token/>
            </itv:GeoLocationToken>
            <itv:RevenueScienceValue>ITVPLAYER.12.18.4</itv:RevenueScienceValue>
            <itv:SessionId/>
            <itv:SsoToken/>
            <itv:UserToken/>
              </tem:userInfo>
              <tem:siteInfo>
            <itv:AdvertisingRestriction>None</itv:AdvertisingRestriction>
            <itv:AdvertisingSite>ITV</itv:AdvertisingSite>
            <itv:AdvertisingType>Any</itv:AdvertisingType>
            <itv:Area>ITVPLAYER.VIDEO</itv:Area>
            <itv:Category/>
            <itv:Platform>DotCom</itv:Platform>
            <itv:Site>ItvCom</itv:Site>
          </tem:siteInfo>
          <tem:deviceInfo>
            <itv:ScreenSize>Big</itv:ScreenSize>
          </tem:deviceInfo>
          <tem:playerInfo>
            <itv:Version>2</itv:Version>
          </tem:playerInfo>
            </tem:GetPlaylist>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
    
        SoapMessage = SM_TEMPLATE%(productionID)
        http = get_httplib()
        
    
        url = 'http://mercury.itv.com/PlaylistService.svc'
        headers = {"Host":"mercury.itv.com","Referer":"http://www.itv.com/mercury/Mercury_VideoPlayer.swf?v=1.6.479/[[DYNAMIC]]/2","Content-type":"text/xml; charset=utf-8","Content-length":"%d" % len(SoapMessage),"SOAPAction":"http://tempuri.org/PlaylistService/GetPlaylist"}
        response, res = http.request("http://mercury.itv.com/PlaylistService.svc", 'POST', headers=headers, body=SoapMessage)
    
        title1= res.split("<ProgrammeTitle>")
        title2= title1[1].split("</ProgrammeTitle>")
    
        #print res
        match2 = re.findall(ur'<PosterFrame>.*?<URL><\!\[CDATA\[(.*?)\].*?</PosterFrame>', res, flags=re.DOTALL)
        #print "match %s" % match2[0]
        if match2:
            thumbfile = match2[0]
        else:
            thumbfile = os.path.join(os.getcwd(), 'icon.png')
        res = re.search('<VideoEntries>.+?</VideoEntries>', res, re.DOTALL).group(0)
        rendition_offset= res.split("rendition-offset=")
        offset_seconds = rendition_offset[1].split(":")
        offset = int(offset_seconds[2])
    
    
        mediafile =  res.split("<MediaFile delivery=")
        there_are_subtitles=0
        match1 = re.findall(ur'<ClosedCaptioningURIs>.*?<URL><\!\[CDATA\[(.*?)\].*?</ClosedCaptioningURIs>', res, flags=re.DOTALL)
        if match1:
            if __settings__.getSetting('subtitles_control') == 'true':
                subtitles_file = download_subtitles(match1[0], offset)
                print "Subtitles at ", subtitles_file
                there_are_subtitles=1
    
        for index in range(len(mediafile)):
            print ("MEDIA ENTRY %d %s"),index, mediafile[index]
    
    
        quality = int(__settings__.getSetting('video_stream'))
        selected_stream = 4
        
        if (quality == 0):
            selected_stream = index 
    
        if (quality == 4):
            if(index==4):
                selected_stream = 4
            else:
                selected_stream = index
        
        if (quality == 3):
            if(index>=3):
                selected_stream = 3
            else:
                selected_stream = index
        
            if (quality == 2):
                    if(index>=2):
                            selected_stream = 2
                    else:
                            selected_stream = index
    
            if (quality == 1):
                    if(index>=1):
                            selected_stream =1 
                    else:
                            selected_stream = index
    
        rtmp = re.compile('(rtmp[^"]+)').findall(res)[0]
        playpath = re.compile('(mp4:[^\]]+)').findall(mediafile[selected_stream])[0]
        rtmp = rtmp.replace('&amp;','&')
    
        url = rtmp + " swfurl=http://www.itv.com/mercury/Mercury_VideoPlayer.swf playpath=" + playpath + " swfvfy=true"
        listitem = xbmcgui.ListItem(name)
        #image_name = pid + '.jpg'
        #thumbfile = os.path.join(IMAGE_DIR, image_name)
        listitem.setThumbnailImage(thumbfile)
        listitem.setInfo('video', {'Title': title2[0],'Premiered' : '2012-01-01','Episode' : '1'})
        play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        play.clear()
        play.add(url,listitem)
        player.play(play)
        pDialog.close()
        if (there_are_subtitles == 1):
            player.setSubtitles(subtitles_file)


def decode_redirect(url):
    
    # some of the the urls passed in are redirects that are not handled by XBMC.
    # These are text files with multiple stream urls

    #if environment in ['xbox', 'linux']:
    #    # xbox xbmc works just fine with redirects
    #    return url

    response = get_url(url).replace('&amp;','&')
    match=re.compile('Ref1\=(http.*)\s').findall(response)

    stream_url = None
    if match:
        stream_url = match[0].rstrip()
    else:
        # no match so pass url to xbmc and see if the url is directly supported 
        stream_url = url

    return stream_url

def decode_date(date):
    # format eg Sat 10 Jan 2009
    (dayname,day,monthname,year) = date.split(' ')
    if not year:
        return date
    month=1
    monthname = monthname.lower()
    lookup = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
    if lookup.has_key(monthname[:3]):
        month=lookup[monthname[:3]]
    
    try:
        # yes I know the colons are weird but the 2009-01-25 xbox release
        # when in filemode (but not library mode) converts YYYY-MM-DD in (YYYY)
        sep='-'
        if environment == 'xbox': sep=':' 
        ndate = "%04d%s%02d%s%02d" % (int(year),sep,int(month),sep,int(day))
    except:
        # oops funny date, return orgional date
        return date
    #print "Date %s from %s" % (ndate, date)
    return ndate

def get_url(url):
    http = get_httplib()
    data = None    
    try:
        resp, data = http.request(url, 'GET')
    except: pass
    
    # second try
    if not data:
        try:
            resp, data = http.request(url, 'GET')
        except: 
            dialog = xbmcgui.Dialog()
            dialog.ok('Network Error', 'Failed to fetch URL', url)
            print 'Network Error. Failed to fetch URL %s' % url
            raise
    
    return data


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

      
def addLink(name,url):
        ok=True
        thumbnail_url = url.split( "thumbnailUrl=" )[ -1 ]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail_url)
        liz.setInfo( type="Video", infoLabels={ "Title": name,'Premiered' : '2012-01-01','Episode' : '1'} )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage,plot='',isFolder=True):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
#        print "addDir " + name
        liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot,'Premiered' : '2012-01-01','Episode' : '7-1' } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
        return ok

def addDir2(name,url,mode,date, episode,iconimage,plot='',isFolder=True):
        print "DATE %s" % date
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
#        print "addDir " + name
        liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot,'Premiered' : date,'Episode' : episode } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
        return ok


params=get_params()
url=None
name=None
mode=None
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print "categories"
        CATS()
elif mode==1:
        print "index of : "+url
        SHOWS(url)
elif mode==2:
        print "Getting Episodes: "+url
        EPS(url)
elif mode==3:
        print "Getting Videofiles: "+url
        VIDEO(url)
elif mode==4:
        print "Getting Videofiles: "+url
        BESTOF(url)
elif mode==5:
        print "Getting Videofiles: "+url
        BESTOFEPS(url)
elif mode==6:
        print "Getting Videofiles: "+url
        STREAMS()



xbmcplugin.endOfDirectory(int(sys.argv[1]))

