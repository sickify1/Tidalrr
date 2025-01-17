#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   scanQueuesArtists.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import pathlib
import time
from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.downloadQueuedTracks import *

import logging

logger = logging.getLogger(__name__)

def scanQueuedPlaylists():
    try:
        playlists = getMonitoredTidalPlaylists()
        if len(playlists) > 0:
            for i, playlist in enumerate(playlists):
                try:
                    if hasattr(playlist, 'uuid'):
                        if playlist.monitored:
                            print('Scanning playlist ', str(i), ' / ',str(len(playlists)), playlist.title)
                            start_playlist(playlist)
                except Exception as e:
                    print("Error scanning playlist: ", e)
    except Exception as e:
        print("Error getting playlists: ", e)


def start_playlist(playlist: Playlist):
    settings = getSettings()
    aigpy.path.mkdirs(settings.downloadPath+'/Playlists')

    print('Scanning playlist ',playlist.title)
    tracks = TIDAL_API.getItems(playlist.uuid, Type.Playlist)
    
    # list only the tracks not downloaded
    tracksToScan, paths = verifyPlaylistTracks(playlist, tracks)

    # Save playlist info to JSON
    generateJSonFile(playlist)

def verifyPlaylistTracks(playlist: Playlist, tidalTracks: [Track]):
    savedTracks = getTidalPlaylistTracks(playlist.uuid)
    tracksToScan = []
    paths = []

    for i, tidalTrack in enumerate(tidalTracks):
        exists = False
        for savedTrack in savedTracks:
            if hasattr(savedTrack, 'id') and tidalTrack.id == savedTrack.id:
                if savedTrack.queued or savedTrack.downloaded:
                    exists = True
        if not exists:
            # track not linked to playlist
            dbTrack = getTidalTrack(tidalTrack.id)
            if not hasattr(dbTrack, 'id'):
                # track not in database
                # also, add it to the db
                tidalTrack.queued = True
                addTidalTrack(tidalTrack)
                tracksToScan.append(tidalTrack)
            elif dbTrack.queued == 0 and dbTrack.downloaded == 0:
                tidalTrack.queued = True
                updateTidalTrack(tidalTrack)
                tracksToScan.append(tidalTrack)

            addTidalPlaylistTrack(playlist.uuid, tidalTrack.id)
            print('Added missing track '+str(i)+'/'+str(len(tidalTracks))+' to DB: '+tidalTrack.title)
        paths.append(tidalTrack.path)

    return tracksToScan, paths

def generateJSonFile(playlist: Playlist):
    aigpy.file.write(playlist.path+'.json', json.dumps(playlist, default=lambda x: x.__dict__), 'w+')

    print('Saved playlist json info to : '+playlist.path+'.json')