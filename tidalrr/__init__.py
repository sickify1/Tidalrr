#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
import sys
import getopt

from events import *
from settings import *
from lidarr import *

def mainCommand():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "holq:u:f:a:", 
                                   ["help", "url", "file", "output", "quality"])
    except getopt.GetoptError as errmsg:
        Printf.err(vars(errmsg)['msg'] + ". Use 'tidalrr -h' for usage.")
        return

    for opt, val in opts:
        if opt in ('-h', '--help'):
            Printf.usage()
            return
        if opt in ('-v', '--version'):
            Printf.logo()
            return
        if opt in ('-u', '--url'):
            use_url(val)
            continue
        if opt in ('-a', '--album'):
            use_text(val)
            continue
        if opt in ('-l', '--lidarr'):
            syncLidarr()
            continue
        if opt in ('-f', '--file'):
            Printf.info('Using file list: '+val)
            file1 = open(val, 'r')
            Lines = file1.readlines()
            count = 0
            # Strips the newline character
            for line in Lines:
                count += 1
                Printf.info("Url #{}: {}".format(count, line.strip()))
                use_url(line.strip())
            continue
        if opt in ('-o', '--output'):
            SETTINGS.downloadPath = val
            SETTINGS.save()
            continue
        if opt in ('-q', '--quality'):
            SETTINGS.audioQuality = SETTINGS.getAudioQuality(val)
            SETTINGS.save()
            continue

def use_url(url):
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        Printf.err(LANG.select.MSG_PATH_ERR + SETTINGS.downloadPath)
        return

    if url is not None:
        if not loginByConfig():
            loginByWeb()
        Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath)
        start(url)

def use_text(txt):
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        Printf.err(LANG.select.MSG_PATH_ERR + SETTINGS.downloadPath)
        return

    if txt is not None:
        if not loginByConfig():
            loginByWeb()
        Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath)
        alb = Album()
        alb.title = txt
        start_album_search(alb)

def syncLidarr():
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        Printf.err(LANG.select.MSG_PATH_ERR + SETTINGS.downloadPath)
        return

    if not loginByConfig():
        loginByWeb()
    Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath)
    albums = [Album()]
    albums = getMissingAlbums(SETTINGS.lidarrURL, SETTINGS.lidarrAPI)

    for a in albums :
        if a.title is not None:    
            # set download path
            SETTINGS.downloadPath = str(a.path)
            start_album_search(a)
    
    Printf.info('Lidarr wanted list synced, go update it.')


def main():
    SETTINGS.read(getProfilePath())
    TOKEN.read(getTokenPath())
    TIDAL_API.apiKey = apiKey.getItem(SETTINGS.apiKeyIndex)
    
    #Printf.logo()
    #Printf.settings()
    
    if len(sys.argv) > 1:
        mainCommand()
        return

    if not apiKey.isItemValid(SETTINGS.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()
    
    Printf.checkVersion()

if __name__ == '__main__':
    # test()
    main()