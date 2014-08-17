#!/usr/bin/python
# -*- coding: utf-8 -*-
import resources.lib._addoncompat as _addoncompat
import resources.lib._common as _common
import resources.lib._contextmenu as _contextmenu
import operator
import os
import sys
import xbmcaddon
import xbmcplugin
import xbmcgui

pluginHandle = int(sys.argv[1])
module_name = "fox"
_common.args.fanart=_common.PLUGINFANART

__plugin__ = 'FOX'
__authors__ = 'BlueCop'
__credits__ = 'moneymaker, slices, zero'
__version__ = '1.0.0'

print '\n\n\n start of CC plugin'

def modes():
	if sys.argv[2] == '':
		_common.args.mode = module_name 
		_common.args.sitemode = "rootlist"
		network = _common.get_network(_common.args.mode)
		if network:
			getattr(network, _common.args.sitemode)()
			if not _common.args.sitemode.startswith('play'):
				xbmcplugin.endOfDirectory(pluginHandle)		
	if _common.args.mode == 'Masterlist':
		print '\n\n\n start of Masterlist'
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.load_showlist()
		_common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == 'Favorlist':   
		print '\n\n\n start of Favorlist'
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.load_showlist(favored = 1)
		_common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == '_contextmenu':
		print '\n\n\n start of contextmenu'
		getattr(_contextmenu, _common.args.sitemode)()
	elif _common.args.mode == '_common':
		print '\n\n\n start of common'
		getattr(_common, _common.args.sitemode)()
	else:
		print '\n\n\n start of else : ' + _common.args.mode + ":" + _common.args.sitemode
		mode = _common.args.mode if hasattr(_common.args, 'mode') else "comedy" 
		sitemode = _common.args.sitemode if hasattr(_common.args, 'sitemode') else "rootlist"
		network = _common.get_network(mode)
		if network:
			getattr(network, sitemode)()
			if not sitemode.startswith('play'):
				xbmcplugin.endOfDirectory(pluginHandle)

if xbmcaddon.Addon("service.network.tunnel").getSetting('enabled') == 'true':
	modes()
	sys.modules.clear()
else:
	dialog = xbmcgui.Dialog()	
	dialog.ok("Plugin Error", "The McIntyreMedia.tv Tunnel or equivalent service is", "required for this plugin") 

