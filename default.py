#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=consider-using-f-string
#
#
"""Takes a screen shot of current playing media and saves as extrafanart or fanartnn.
Intent is to use the screenshot as a random background fanart (requires skin support)
either by multiimage using the extrafanart folder, or randomized fadelabel using
fanartnn convention.
"""

import os
import re

import xbmc
import xbmcaddon
import xbmcgui
from PIL import Image

MAX_FANARTS = 200
LOG_LEVEL = [xbmc.LOGDEBUG, xbmc.LOGWARNING, xbmc.LOGINFO]
__addon__ = xbmcaddon.Addon()
__addon_id__ = __addon__.getAddonInfo('id')

class Main:
    """All processing happens in the class
    """
    def __init__(self) -> None:
        """Constructor creates a Main instance with addon setting to toggle
        use of extrafanart folder, then takes a screenshot, converts to jpg (to
        conserve space) and saves as screenshot or fanart as appropriate.
        Note:  xbmcAddon Settings class not used for Matrix compatability.
        """
        use_folderarts: bool = __addon__.getSettingBool('use_extrafanart_folder')
        self.log(f' Taking screenshot with extrafanart {str(use_folderarts).upper()}', LOG_LEVEL[2])
        self.get_screenshot(use_folderarts)

    def log(self, msg: str, level: int=LOG_LEVEL[0]) -> None:
        """wraps Kodi log function

        Args:
            msg (str): string to write to debug log
            level (str) either DEBUG, WARNING, or INFO
        """
        xbmc.log(f'{__addon_id__}: {msg}', level)


    def get_screenshot(self, use_folderarts: bool) -> None:
        """takes a screenshot and saves file as jpg in appropiate folder

        Args:
            use_folderarts (bool): switch betweeen extrafanart and fanartnn styles
        """
        if (xbmc.getCondVisibility('VideoPlayer.Content(episodes)')
                or xbmc.getCondVisibility('VideoPlayer.Content(files)')):
            current_folder = xbmc.getInfoLabel('Player.Folderpath')
        else:
            current_folder = xbmc.getInfoLabel('Player.Folderpath')
        if (not xbmc.getCondVisibility('Player.HasMedia')
                or xbmc.getCondVisibility('Player.IsInternetStream')):
            self.log('No valid save location for screenshot', LOG_LEVEL[1])
            return
        self.log(f'Current playing media folder path: {current_folder}')
        current_folder = current_folder.replace('\\', '/')
        if use_folderarts:
            shot_folder = current_folder + 'extrafanart/'
        else:
            shot_folder = current_folder
        unc_folder = shot_folder.lstrip('smb:')
        if not os.path.exists(unc_folder):
            os.mkdir(unc_folder)
            self.log(f'Created new folder {unc_folder}')
        str_shot_folder =  '\"' + shot_folder + '\"'
        # set the screenshot folder in Kodi
        response = xbmc.executeJSONRPC('{"jsonrpc":"2.0", '
                                        '"method":"Settings.SetSettingValue",'
                                        '"params": {'
                                            '"setting": "debug.screenshotpath", '
                                            '"value":  %s}, '
                                        '"id":1}' % str_shot_folder)

        if 'result' in response:
            xbmc.executebuiltin('TakeScreenshot')
            notify_dialog = xbmcgui.Dialog()
            notify_dialog.notification('Screenshot','','',1000)
        shot_pattern = re.compile(r'screenshot(\d+)\.png')
        jpg_shot_pattern = re.compile(r'screenshot(\d+)\.jpg')
        fanart_pattern = re.compile(r'fanart(\d+)')
        xbmc.sleep(500) #ensure screenshot has been saved
        screenshot_files: list = [png_file for png_file in os.listdir(unc_folder)
                                  if shot_pattern.fullmatch(png_file)]
        maxfile: int = 0
        jpgmaxfile: int = 0
        # get list of all screenshotnnnn.jpg files in folder and find max nnnn
        jpg_files: list = [jpg_file for jpg_file in os.listdir(unc_folder)
                           if jpg_shot_pattern.fullmatch(jpg_file)]
        for jpg_file in jpg_files:
            if int(jpg_shot_pattern.search(jpg_file).group(1)) > jpgmaxfile:
                jpgmaxfile = int(jpg_shot_pattern.search(jpg_file).group(1))
        #convert image from png to jpg and save then delete png file
        for file in screenshot_files:
            try:
                with Image.open(unc_folder + file) as image:
                    image = image.convert('RGB')
                    newfile = 'screenshot' + str(jpgmaxfile +1).zfill(4) + '.jpg'
                    image.save(unc_folder + newfile)
                jpgmaxfile = jpgmaxfile +1
                os.remove(unc_folder + file)
                if use_folderarts:
                    self.log(f'{newfile} added to extrafanart folder', LOG_LEVEL[2])
                else:
                    # rename screenshotmm.jpg to fanartnn+1.jpg where nn is current max fanart
                    fanart_files: list = [fanart for fanart in os.listdir(unc_folder)
                                    if fanart_pattern.fullmatch(fanart.split('.')[0])]
                    # get the max fanartnn.jpg nn value so new fanart can be added as next nn
                    for fanart_file in fanart_files:
                        if int(fanart_pattern.search(fanart_file).group(1)) > maxfile:
                            maxfile = int(fanart_pattern.search(fanart_file).group(1))
                    os.rename(unc_folder + newfile, unc_folder + 'fanart'
                                + str(maxfile + 1) + '.jpg')
                    self.log(f'screenshot added as fanart{str(maxfile + 1)}.jpg', LOG_LEVEL[2])
            except IOError as ioerror:
                self.log(f'Unable to process {file} due to {ioerror}', LOG_LEVEL[1])


if __name__ == "__main__":
    Main()
