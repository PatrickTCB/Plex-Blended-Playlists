import os
import json
import random
import sys
import time
import tomllib
from lib import plex, common

def usersEligibleSongs(plexhost, plextoken, playlistIDs, ignoredSongIDs, verbose):
    tracks = []
    for playlistID in playlistIDs:
        playlist = plex.getSinglePlaylist(plexhost=plexhost, plextoken=plextoken, playlistid=playlistID)
        if "Track" in playlist["MediaContainer"].keys():
            if isinstance(playlist["MediaContainer"]["Track"], list):
                for track in playlist["MediaContainer"]["Track"]:
                    if track["@ratingKey"] not in ignoredSongIDs:
                        tracks.append(track)
                    else:
                        if verbose:
                            print("'{}' by '{}' is in ignoredSongIDs.".format(track["@title"], track["@grandparentTitle"]))
    return tracks
        

def existingBlendedList(plexhost, plextoken, blendedListName) -> dict:
    result = {}
    userPlaylists = plex.getAllPlaylists(plexhost, plextoken)
    blendedListExists = False
    blendedListId = 0
    blendedListSongs = []
    titlesFound = []
    for playlist in userPlaylists["MediaContainer"]["Playlist"]:
        titlesFound.append(playlist["@title"])
        if blendedListName == playlist["@title"]:
            blendedListExists = True
            blendedListId = playlist["@ratingKey"]
            p = plex.getSinglePlaylist(plexhost=u["host"], plextoken=u["token"], playlistid=playlist["@ratingKey"])
            if p:
                if "MediaContainer" in p.keys():
                    if int(p["MediaContainer"]["@size"]) > 0:
                        try:
                            for song in p["MediaContainer"]["Track"]:
                                blendedListSongs.append(song["@ratingKey"])
                        except:
                            blendedListSongs.append(p["MediaContainer"]["Track"]["@ratingKey"])
    result["blendedListID"] = blendedListId
    result["blendedListSongs"] = blendedListSongs
    result["blendedListExists"] = blendedListExists
    return result

def ignoreThisSong(ignoredSongs, compareSong):
    for song in ignoredSongs:
        ignoreThis = True
        if song["title"] != compareSong["title"]:
            ignoreThis = False
        if song["artist"] != compareSong["artist"]:
            ignoreThis = False
        if song["album"] != compareSong["album"]:
            ignoreThis = False
        if ignoreThis:
            return True
    return False

a = common.parseArgs(sys.argv)
currentPath = os.path.realpath(__file__).replace("main.py", "")

confFileName = "{}conf.toml".format(currentPath)
if "conf" in a.keys():
    confFileName = a["conf"]

blendsFileName = "{}blends.json".format(currentPath)
if "blends" in a.keys():
    blendsFileName = a["conf"]["blends"]

dryRun = "dryRun" in a.keys()

# Load configs
confstring = common.fileToString(confFileName)
conf = tomllib.loads(confstring)

blendsConfString = common.fileToString(blendsFileName)
blends = json.loads(blendsConfString)

# Setup icecream / debugging stuff
verbose = False
printEnd = "\r"
textCutOff = 20
if a["v"]:
    verbose = True
    printEnd = "\n"
    textCutOff = 500

# First get the list of songs for the playlist

goalNumberOfSongs = conf["settings"]["numberOfSongs"]

ignoredSongs = []
ignoredSongIDs = []
try:
    ignoredSongs = json.loads(common.fileToString("{}ignoredSongs.json".format(currentPath)))
except:
    if verbose:
        print("Couldn't parse ignoredSongs.json.")

for blend in blends["blends"]:
    songsPerUser = int(goalNumberOfSongs / len(blend["users"]))
    blendPlaylistName = blend["name"]
    random.shuffle(blend["users"])
    blendPlaylistSongs = []
    if conf["settings"]["allowDuplicatesAcrossLists"]:
        ignoredSongIDs = []
    for u in blend["users"]:
        startTime = time.time()
        print("Searching for {}'s songs for {}".format(u["name"].title(), blend["name"]))
        if verbose:
            print("Building from {} playlists".format(len(u["playlists"])))
        candidateSongs = []
        bl = existingBlendedList(plexhost=u["host"], plextoken=u["token"], blendedListName=blendPlaylistName)
        ignoredSongIDs.extend(bl["blendedListSongs"])
        u["bl"] = bl
        userSongs = usersEligibleSongs(plexhost=u["host"], plextoken=u["token"], playlistIDs=u["playlists"], ignoredSongIDs=ignoredSongIDs, verbose=verbose)
        if len(userSongs) == 0:
            print("Somehow {} has no eligible songs. This is likely the result of a misconfiguration. Please check you blends.json file.")
            sys.exit(3)
        print("Looking for {} songs out of {} options for {}.".format(songsPerUser, len(userSongs), u["name"]))
        while len(candidateSongs) < songsPerUser:
            song = random.choice(userSongs)
            ignorableDict = {
                "title": song["@title"],
                "artist": song["@grandparentTitle"],
                "album": song["@parentTitle"]
            }
            songAllowed = True
            songAllowed = not ignoreThisSong(ignoredSongs=ignoredSongs, compareSong=ignorableDict)
            if songAllowed:
                songAllowed = song["@ratingKey"] not in ignoredSongIDs
            if songAllowed:
                if song["@ratingKey"] not in candidateSongs and song["@ratingKey"] not in blendPlaylistSongs:
                    candidateSongs.append(song["@ratingKey"])
                userSongs.remove(song)
            timeNow = time.time()
            timeSpent = int(timeNow - startTime)
            if timeSpent > conf["settings"]["songSearchTimeLimit"]:
                print("\nTimeout on song search for {}".format(u["name"]))
                break
            if len(userSongs) == 0:
                break
        print("Found {} candidate songs for {}".format(len(candidateSongs), u["name"]))
        ignoredSongIDs.extend(candidateSongs)
        blendPlaylistSongs.extend(candidateSongs)

    print("\nThe playlist '{}' will have {} items".format(blendPlaylistName, len(blendPlaylistSongs)))
    random.shuffle(blendPlaylistSongs)
    # Check to see if the blend playlist already exists for each user
    for u in blend["users"]:
        bl = u["bl"]
        print("\nAdding {} songs to {} (id {}) for {}".format(len(blendPlaylistSongs), blendPlaylistName, bl["blendedListID"], u["name"].title()))
        if dryRun == False:
            if bl["blendedListExists"] and len(bl["blendedListSongs"]) > 0:
                plex.removeAllFromPlaylist(plexhost=u["host"], plextoken=u["token"], playlistid=bl["blendedListID"], verbose=verbose)
            if bl["blendedListID"] == 0:
                blendedList = plex.newPlaylist(plexhost=u["host"], plextoken=u["token"], title=blendPlaylistName)
                bl["blendedListID"] = blendedList["MediaContainer"]["Playlist"]["@ratingKey"]
            if bl["blendedListID"] != 0:
                for songID in blendPlaylistSongs:
                    plex.addItemToPlaylist(plexhost=u["host"], plextoken=u["token"], playlistId=bl["blendedListID"], itemId=songID)
        else:
            print("Just a dry run. No playlists were harmed during the running of this script.")