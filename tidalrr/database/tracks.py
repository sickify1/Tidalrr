#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   database.py
@Time    :   2023/10/18
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import sqlite3
from tidalrr.model import *
from tidalrr.database.albums import getArtistsNameJSON
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()

def addTidalTrack(track=Track):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_tracks (id, title, duration, trackNumber, volumeNumber, trackNumberOnPLaylist, version, isrc,\
                 explicit, audioQuality, audioModes, copyRight, artist, artists, album, url, path, queued, downloaded, plexUUID)\
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    track.id,
                    track.title,
                    track.duration,
                    track.trackNumber,
                    track.volumeNumber,
                    track.trackNumberOnPlaylist,
                    track.version,
                    track.isrc,
                    track.explicit,
                    track.audioQuality,
                    track.audioModes,
                    track.copyRight,
                    track.artist,
                    track.artists,
                    track.album,
                    track.url,
                    track.path,
                    track.queued,
                    track.downloaded,
                    track.plexUUID
                ))
    connection.commit()
    connection.close()

def updateTidalTrack(track=Track):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_tracks SET queued = ?, downloaded = ?, plexUUID = ? WHERE id = ?",
                (track.queued, track.downloaded, track.plexUUID, track.id))
    connection.commit()
    connection.close()

def updateTidalTrackPath(track=Track):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_tracks SET path = ?WHERE id = ?",
                (track.path, track.id))
    connection.commit()
    connection.close()

def getTidalTracks() -> [Track]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_tracks.* FROM tidal_tracks\
                        inner join tidal_albums on tidal_albums.id = tidal_tracks.album\
                        inner join tidal_artists on tidal_artists.id = tidal_albums.artist\
                         WHERE tidal_tracks.id IS NOT NULL\
                        ORDER BY tidal_artists.name, tidal_albums.title, tidal_tracks.volumeNumber, tidal_tracks.trackNumber').fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0:
        for track in rows:
            t = convertToTrack(track)
            t.artists = getArtistsNameJSON(t.artists)
            new_rows.append(t)
    return new_rows

def getQueuedTidalTracks() -> [Track]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_tracks.* FROM tidal_tracks\
                        inner join tidal_albums on tidal_albums.id = tidal_tracks.album\
                        inner join tidal_artists on tidal_artists.id = tidal_albums.artist\
                         WHERE tidal_tracks.id IS NOT NULL AND tidal_tracks.queued = 1\
                        ORDER BY tidal_artists.name, tidal_albums.title, tidal_tracks.volumeNumber, tidal_tracks.trackNumber').fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0:
        for track in rows:
            t = convertToTrack(track)
            t.artists = getArtistsNameJSON(t.artists)
            new_rows.append(t)
    return new_rows

def getTracksForAlbum(albumId) -> [Track]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_tracks.* FROM tidal_tracks\
                        inner join tidal_albums on tidal_albums.id = tidal_tracks.album\
                        inner join tidal_artists on tidal_artists.id = tidal_albums.artist\
                         WHERE tidal_tracks.id IS NOT NULL AND tidal_tracks.album = ?\
                        ORDER BY tidal_artists.name, tidal_albums.title, tidal_tracks.volumeNumber, tidal_tracks.trackNumber', (albumId,)).fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0:
        for track in rows:
            t = convertToTrack(track)
            t.artists = getArtistsNameJSON(t.artists)
            new_rows.append(t)
    return new_rows

def getTidalTrack(id=int) -> Track:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_tracks WHERE id = ?',(id,)).fetchone()
    conn.close()
    track = None
    if row is not None:
        track = convertToTrack(row)
        track.artists = getArtistsNameJSON(track.artists)
    return track

def delTidalTrack(id=str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM tidal_tracks WHERE id = ?', (id,))
    conn.commit()
    conn.close()