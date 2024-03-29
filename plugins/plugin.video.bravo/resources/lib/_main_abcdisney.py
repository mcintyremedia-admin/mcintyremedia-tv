﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import os
import re
import simplejson
import sys
import time
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SHOWS = 'http://api.watchabc.go.com/vp2/ws/s/contents/2015/shows/jsonp/%s/001/-1'
VIDEOLIST = 'http://api.watchabc.go.com/vp2/ws/s/contents/2015/videos/jsonp/%s/'
VIDEOURL = 'http://api.watchabc.go.com/vp2/ws/s/contents/2015/videos/jsonp/%s'
PLAYLISTMOV = 'http://www.kaltura.com/p/%s/sp/%s00/playManifest/format/rtmp/entryId/'
PLAYLISTMP4 = 'http://www.kaltura.com/p/%s/sp/%s00/playManifest/format/applehttp/entryId/'
CLOSEDCAPTIONHOST = 'http://cdn.video.abc.com'
GETAUTHORIZATION = 'http://api.watchabc.go.com/vp2/ws-secure/entitlement/2015/authorize/json'
SWFURL = 'http://livepassdl.conviva.com/ver/2.61.0.65970/LivePassModuleMain.swf'
BITRATETABLE = {	60 : 'a',
					110 : 'b',
					190 : 'c',
					360 : 'd',
					590 : 'e',
					1010 : 'f',
					2100 : 'g' }

def masterlist(SITE, BRANDID):
	master_db = []
	master_data = _connection.getURL(SHOWS % BRANDID)
	master_menu = simplejson.loads(master_data)['shows']['show']
	for master_item in master_menu:
		fullepisodes = 0
		clips = 0
		if (int(master_item['clips']['count']['@total']) + int(master_item['fullepisodes']['count']['@total'])) > 0:
			if int(master_item['clips']['count']['@total']) > 0:
				try:
					if int(master_item['clips']['count']['video']['@accesslevel']) == 0:
						clips = int(master_item['clips']['count']['video']['$'])	
				except:
					if int(master_item['clips']['count']['video'][0]['@accesslevel']) == 0:
						clips = int(master_item['clips']['count']['video'][0]['$'])
			if int(master_item['fullepisodes']['count']['@total']) > 0:
				try:
					if int(master_item['fullepisodes']['count']['video']['@accesslevel']) == 0:
						fullepisodes = int(master_item['fullepisodes']['count']['video']['$'])
				except:
					if int(master_item['fullepisodes']['count']['video'][0]['@accesslevel']) == 0:
						fullepisodes = int(master_item['fullepisodes']['count']['video'][0]['$'])
			if (fullepisodes + clips) > 0:
				master_name = master_item['title'].strip()
				season_url = master_item['@id']
				master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(SITE, BRANDID):
	xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
	season_url = _common.args.url
	season_menu = []
	season_numbers = []
	clip_numbers = []
	season_url2 = VIDEOLIST % BRANDID + '001/-1/' + season_url + '/-1/-1/-1/-1'
	season_data = _connection.getURL(season_url2)
	season_data2 = simplejson.loads(season_data)['videos']
	season_count = int(season_data2['@count'])
	if season_count > 1:
		season_menu = season_data2['video']
	elif season_count == 1:
		season_menu.append(dict(season_data2['video']))
	for season_item in season_menu:
		if int(season_item['@accesslevel']) == 0:
			if season_item['@type'] == 'lf':
				try:
					if season_item['season']['@id'] not in season_numbers:
						season_numbers.append(season_item['season']['@id'])
						season_name = 'Season ' + season_item['season']['@id']
						season_url3 = VIDEOLIST % BRANDID + '001/' + season_item['@type'] + '/' + season_url + '/' + season_item['season']['@id'] + '/-1/-1/-1'
						_common.add_directory(season_name, SITE, 'episodes', season_url3)
				except:
					pass
			elif season_item['@type'] == 'sf':
				try:
					if season_item['season']['@id'] not in clip_numbers:
						clip_numbers.append(season_item['season']['@id'])
						season_name = 'Season Clips ' + season_item['season']['@id']
						season_url4 = VIDEOLIST % BRANDID + '001/' + season_item['@type'] + '/' + season_url + '/' + season_item['season']['@id'] + '/-1/-1/-1'
						_common.add_directory(season_name, SITE, 'episodes', season_url4)
				except:
					pass
	_common.set_view('seasons')

def episodes(SITE):
	episode_menu = []
	episode_data = _connection.getURL(_common.args.url)
	episode_data2 = simplejson.loads(episode_data)['videos']
	episode_count = int(episode_data2['@count'])
	if episode_count > 1:
		episode_menu = episode_data2['video']
	elif episode_count == 1:
		episode_menu.append(dict(episode_data2['video']))
	for episode_item in episode_menu:
		if int(episode_item['@accesslevel']) == 0:
			highest_height = -1
			episode_name = episode_item['title']
			episode_duration = int(episode_item['duration']['$']) / 1000
			season_number = episode_item['season']['@id']
			episode_id = episode_item['@id']
			episode_type = episode_item['@type']
			try:
				episode_description = _common.replace_signs(episode_item['longdescription'])
			except:
				episode_description = _common.replace_signs(episode_item['description'])
			try:
				episode_airdate = episode_item['airdates']['airdate'].rsplit(' ',1)[0]
				episode_airdate = _common.format_date(episode_airdate,'%a, %d %b %Y %H:%M:%S', '%d.%m.%Y')
			except:
				try:
					episode_airdate = episode_item['airdates']['airdate'][0].rsplit(' ',1)[0]
					episode_airdate = _common.format_date(episode_airdate,'%a, %d %b %Y %H:%M:%S', '%d.%m.%Y')
				except:
					episode_airdate = -1
			try:
				episode_number = episode_item['number']
			except:
				episode_number = -1
			try:
				for episode_picture in episode_item['thumbnails']['thumbnail']:
					try:
						picture_height = int(episode_picture['@width'])
					except:
						if episode_picture['@type'] == 'source-16x9':
							picture_height = 720
						else:
							picture_height = 0
					if picture_height > highest_height:
						highest_height = picture_height
						episode_thumb = episode_picture['$']
			except:
				episode_thumb = episode_item['thumbnails']['thumbnail']['$']
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(episode_id) + '#' + urllib.quote_plus(episode_type) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={'title' : episode_name,
						'plot' : episode_description,
						'premiered' : episode_airdate,
						'durationinseconds' : episode_duration,
						'episode' : episode_number,
						'season' : season_number }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def play_video(SITE, BRANDID, PARTNERID):
	video_id, video_type = _common.args.url.split('#')
	hbitrate = -1
	lbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality'))
	localhttpserver = False
	video_auth = get_authorization(BRANDID, video_id, video_type)
	if video_auth is False:
		video_url = VIDEOLIST % BRANDID + '001/-1/-1/-1/' + video_id + '/-1/-1'
		video_data = _connection.getURL(video_url)
		try:
			video_data2 = simplejson.loads(video_data)['videos']['video']
			video_format = video_data2['assets']['asset'][0]['@format']
			video_closedcaption = video_data2['closedcaption']['@enabled']
		except:
			try:
				video_data2 = simplejson.loads(video_data)['videos']['video']
				video_format = video_data2['assets']['asset']['@format']
				video_closedcaption = video_data2['closedcaption']['@enabled']
			except:
				video_format = 'MOV'
				video_closedcaption = 'false'
		video_id = video_id.replace('VDKA','')
		if video_format == 'MP4':
			video_url = PLAYLISTMP4 % (PARTNERID, PARTNERID) + video_id
			video_data = _connection.getURL(video_url)
			video_url2 = _m3u8.parse(video_data)
			for video_index in video_url2.get('playlists'):
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				if bitrate > hbitrate and bitrate <= (sbitrate * 1000):
					hbitrate = bitrate
					playpath_url = video_index.get('uri')
			finalurl = playpath_url
		elif  video_format == 'MOV':
			playpath_url = None
			video_url = PLAYLISTMOV % (PARTNERID, PARTNERID) + video_id
			video_data = _connection.getURL(video_url)
			video_tree = BeautifulSoup(video_data)
			base_url = video_tree('baseurl')[0].string
			video_url2 = video_tree.findAll('media')
			for video_index in video_url2:
				bitrate = int(video_index['bitrate'])
				if bitrate < lbitrate or lbitrate == -1:
					lbitrate = bitrate
					lplaypath_url = video_index['url']	
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					playpath_url = video_index['url']
			if playpath_url is None:
				playpath_url = lplaypath_url
			finalurl = base_url + ' playpath=' + playpath_url + ' swfUrl=' + SWFURL + ' swfVfy=true'
	else:
		video_url = VIDEOLIST % BRANDID + '002/-1/-1/-1/' + video_id + '/-1/-1'
		video_data = _connection.getURL(video_url)
		video_data2 = simplejson.loads(video_data)['videos']['video']
		video_closedcaption = video_data2['closedcaption']['@enabled']
		try:
			video_url2 = video_data2['assets']['asset']['$'] + video_auth
		except:
			video_url2 = video_data2['assets']['asset'][1]['$'] + video_auth
		video_data3 = _connection.getURL(video_url2.replace('m3u8','json'))
		video_url3 = simplejson.loads(video_data3)
		for video_keys in BITRATETABLE.iterkeys():
			bitrate = int(video_keys)
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				video_url4 = video_url3['url'].replace('__ray__', BITRATETABLE[video_keys])
		video_url4 = video_url4.replace('https','http').replace('json','m3u8')
		video_data4 = re.sub(r"\#EXT-X-DISCONTINUITY\n","", _connection.getURL(video_url4))
		key_url = re.compile('URI="(.*?)"').findall(video_data4)[0]
		key_data = _connection.getURL(key_url)		
		key_file = open(_common.KEYFILE, 'wb')
		key_file.write(key_data)
		key_file.close()
		localhttpserver = True
		filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH,'_proxy.py') + ', 12345)'
		xbmc.executebuiltin(filestring)
		time.sleep(20)
		video_data4 = video_data4.replace(key_url, 'http://127.0.0.1:12345/play.key')
		playfile = open(_common.PLAYFILE, 'w')
		playfile.write(video_data4)
		playfile.close()
		finalurl = _common.PLAYFILE
	if (video_closedcaption == 'true') and (_addoncompat.get_setting('enablesubtitles') == 'true'):
		try:
			closedcaption = CLOSEDCAPTIONHOST + video_data2['closedcaption']['src']['$'].split('.com')[1]
			convert_subtitles(closedcaption)
		except:
			video_closedcaption = 'false'
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (video_closedcaption != 'false'):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLE)
	if localhttpserver is True:
		time.sleep(100)
		try:
			_connection.getURL('http://localhost:12345/stop', connectiontype = 0)
		except:
			pass

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	sub = br.sub('\n', str(data))
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = _connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(_common.smart_utf8(line))
			start_time_hours, start_time_rest = line['begin'].split(':', 1)
			start_time_hours = '%02d' % (int(start_time_hours) - 1)
			start_time = _common.smart_utf8(start_time_hours + ':' + start_time_rest.replace('.', ','))
			end_time_hours, end_time_rest = line['end'].split(':', 1)
			end_time_hours = '%02d' % (int(end_time_hours) - 1)
			end_time = _common.smart_utf8(end_time_hours + ':' + end_time_rest.replace('.', ','))
			str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
	file = open(_common.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
	return True

def get_authorization(brandid, video_id, video_type):
	auth_time = time.time()
	parameters = {	'video_id' : video_id,
					'__rnd' : auth_time,
					'device' : '001',
					'brand' : brandid,
					'video_type' : video_type }
	auth_data = _connection.getURL(GETAUTHORIZATION, parameters)
	try:
		auth_sig = '?' + simplejson.loads(auth_data)['entitlement']['uplynk']['sessionKey']
	except:
		auth_sig = False
	return auth_sig
