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
module_name = "oxygen"
_common.args.fanart=_common.PLUGINFANART

__plugin__ = 'Oxygen'
__authors__ = 'McIntyreMedia.tv,BlueCop'
__credits__ = 'moneymaker, slices, zero'
__version__ = '1.0.4'


def modes():
	if sys.argv[2] == '':
		_common.args.mode = module_name 
		_common.args.sitemode = "rootlist"
		network = _common.get_network(_common.args.mode)
		all_description = ''
		count = 0
		network_name = network.NAME
		station_icon = os.path.join(_common.IMAGEPATH, network.SITE + '.png')		
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.root_list(_common.args.mode)
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == 'Masterlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.load_showlist()
		_common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == 'Favorlist':   
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.load_showlist(favored = 1)
		_common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == '_contextmenu':
		getattr(_contextmenu, _common.args.sitemode)()
	elif _common.args.mode == '_common':
		getattr(_common, _common.args.sitemode)()
	else:
		network = _common.get_network(_common.args.mode)
		if network:
			getattr(network, _common.args.sitemode)()
			if not _common.args.sitemode.startswith('play'):
				xbmcplugin.endOfDirectory(pluginHandle)

if xbmcaddon.Addon("service.network.tunnel").getSetting('enabled') == 'true':
	modes()
	sys.modules.clear()
else:
	dialog = xbmcgui.Dialog()	
	dialog.ok("Plugin Error", "The McIntyreMedia.tv Tunnel or equivalent service is", "required for this plugin") 

