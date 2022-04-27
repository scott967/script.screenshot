#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#

import xbmc, xbmcgui
import os

if xbmc.getCondVisibility('VideoPlayer.Content(episodes)') or xbmc.getCondVisibility('VideoPlayer.Content(files)') :
    current_folder = 'T:/Streams/TV/' + xbmc.getInfoLabel('VideoPlayer.TVShowTitle')  + '/'
else: current_folder = xbmc.getInfoLabel('Player.Folderpath')
xbmc.log('getLabel: ' + current_folder)
current_folder = current_folder.replace('\\', '/')
xbmc.log('encode utf-8: ' + current_folder)
shot_folder = current_folder + 'extrafanart/'

xbmc.log('shot folder: ' + shot_folder)
UNC_folder = shot_folder.lstrip('smb:')
xbmc.log('UNC folder: ' + UNC_folder)
if not os.path.exists(UNC_folder):
    os.mkdir(UNC_folder)
    xbmc.log('Created new folder ')
str_shot_folder =  '\"' + shot_folder + '\"'
xbmc.log('Enc shot folder: ' + str_shot_folder)
response = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params": {"setting": "debug.screenshotpath", "value":  %s}, "id":1}' %str_shot_folder)
#  if (response['result']) xbmc.executebuiltin(TakeScreenshot)
notify_dialog = xbmcgui.Dialog()
xbmc.executebuiltin('TakeScreenshot')
notify_dialog.notification('Screenshot','','',1000)


