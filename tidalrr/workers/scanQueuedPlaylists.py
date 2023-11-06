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

from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.scanQueuedTracks import *

def scanQueuedPlaylists():
    playlists = getTidalPlaylists()
    if len(playlists) > 0 :
        for i,playlist in enumerate(playlists):
            if hasattr(playlist, 'uuid'):
                if playlist.queued:
                    print('Scanning playlist '+ str(i)+'/'+str(len(playlists))+' '+playlist.title)
                    start_playlist(playlist)
                    playlist.queued = False
                    updateTidalPlaylist(playlist)

def start_playlist(obj: Playlist):
    # save this to playlist.json
    #path = getPlaylistPath(obj)
    settings = getSettings()
    aigpy.path.mkdirs(settings.downloadPath+'/Playlists')

    aigpy.file.write(obj.path+'.json', json.dumps(obj, default=lambda x: x.__dict__), 'w+')

    print('Saved playlist json info to : '+obj.path+'.json')
    paths = []
    tracks = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    for index,track in enumerate(tracks):
        #check if artist exists
        if not hasattr(getTidalArtist(track.artist), 'id'):
            # insert artist in db
            try:
                trackArtist = TIDAL_API.getArtist(track.artist)
                addTidalArtist(trackArtist)
            except:
                print('Track artist dosent exist on Tidal, skipping track')
                continue
        #same for album
        if not hasattr(getTidalAlbum(track.album), 'id'):
            # insert artist in db
            addTidalAlbum(TIDAL_API.getAlbum(track.album))
        track.queued = True
        addTidalTrack(track)

        itemAlbum = getTidalAlbum(track.album)
        if itemAlbum is None:
            track.trackNumberOnPlaylist = index + 1
        path = scanTrackPath(track, itemAlbum, obj)[1]
        if path != '':
            paths.append(path)

    with open(obj.path+'.m3u', 'w+') as f:
        #f.write('#EXTM3U\n')
        for i,item in enumerate(paths, start=1):
            f.write(item+'\n')
    print('Done generating m3u playlist file: '+obj.path+'.m3u')

    # Generate the playlist file
    with open(obj.path+'.m3u8', 'w+') as f:
        f.write('#EXTM3U\n')
        for i,item in enumerate(tracks, start=1):
            artist = getTidalArtist(item.artist)
            if hasattr(artist, 'id'):
                f.write(f'#EXTINF:{item.duration},{artist.name} - {item.title}\n')
                f.write(item.path+'\n') 
    print('Done generating m3u8 playlist file: '+obj.path+'.m3u8')
    scanQueuedTracks()

def writePlaylistInfos(tracks, album: Album = None, playlist : Playlist=None):
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        settings = getSettings()
        if settings.saveCovers and not settings.usePlaylistFolder:
            scanCover(album)
        return album
    
    for index, item in enumerate(tracks):
        itemAlbum = album
        if itemAlbum is None:
            itemAlbum = __getAlbum__(item)
            item.trackNumberOnPlaylist = index + 1
        addTidalTrack(item)
