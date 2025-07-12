import os
import json
import random
import sys
import time
import tomllib
from lib import plex, common

def existingBlendedList(plexhost, plextoken, blendedListName) -> dict:
    result = {}
    userPlaylists = plex.getAllPlaylists(plexhost, plextoken)
    blendedListExists = False
    blendedListId = 0
    blendedListSongs = []
    for playlist in userPlaylists["MediaContainer"]["Playlist"]:
        if blendPlaylistName == playlist["@title"]:
            blendedListExists = True
            blendedListId = playlist["@ratingKey"]
            p = plex.getSinglePlaylist(plexhost=u["host"], plextoken=u["token"], playlistid=playlistID)
            common.stringToFile("playlists.json", json.dumps(p))
            try:
                for song in p["MediaContainer"]["Track"]:
                    blendedListSongs.append(song["@ratingKey"])
            except:
                blendedListSongs.append(p["MediaContainer"]["Track"]["@ratingKey"])
    if blendedListExists:
        plex.removeAllFromPlaylist(plexhost=u["host"], plextoken=u["token"], playlistid=blendedListId, verbose=verbose)
    result["blendedListID"] = 0
    result["blendedListSongs"] = blendedListSongs    
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

usersFileName = "{}users.toml".format(currentPath)
if "users" in a.keys():
    usersFileName = a["conf"]

# Load configs
confstring = common.fileToString(confFileName)
conf = tomllib.loads(confstring)

usersConfString = common.fileToString(usersFileName)
users = tomllib.loads(usersConfString)

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
blendPlaylistName = str("{} blend".format("/".join(users.keys()))).title()
blendPlaylistSongs = []

ignoredSongs = []
try:
    ignoredSongs = json.loads(common.fileToString("{}ignoredSongs.json".format(currentPath)))
except:
    if verbose:
        print("Couldn't parse ignoredSongs.json.")


songsPerUser = int(goalNumberOfSongs / len(users.keys()))
startTime = time.time()
usersList = list(users.keys())
random.shuffle(usersList)
for k in usersList:
    u = users[k]
    print("Adding {}'s songs".format(k.title()))
    if verbose:
        print("Building from {} playlists".format(len(u["playlists"])))
    candidateSongs = []
    playlistsChecked = 0
    while len(candidateSongs) < songsPerUser:
        playlistID = random.choice(u["playlists"])
        print("Looking at {} for {}.          ".format(playlistID, k), end=printEnd)
        playlist = plex.getSinglePlaylist(plexhost=u["host"], plextoken=u["token"], playlistid=playlistID)
        song = random.choice(playlist["MediaContainer"]["Track"])
        ignorableDict = {
            "title": song["@title"],
            "artist": song["@grandparentTitle"],
            "album": song["@parentTitle"]
        }
        bl = existingBlendedList(plexhost=u["host"], plextoken=u["token"], blendedListName=blendPlaylistName)
        blendedListExists = (bl["blendedListID"] != 0)
        blendedListId = bl["blendedListID"]
        blendedListSongs = bl["blendedListSongs"]
        if ignoreThisSong(ignoredSongs=ignoredSongs, compareSong=ignorableDict) == False or song["@ratingKey"] not in blendedListSongs:
            if song["@ratingKey"] not in candidateSongs and song["@ratingKey"] not in blendPlaylistSongs:
                candidateSongs.append(song["@ratingKey"])
            playlist["MediaContainer"]["Track"].remove(song)
        print("There are now {} candidate songs.                ".format(len(candidateSongs)), end=printEnd)
        playlistsChecked = playlistsChecked + 1
        timeNow = time.time()
        timeSpent = int(timeNow - startTime)
        if timeSpent > conf["settings"]["songSearchTimeLimit"]:
            print("\nTimeout on song search for {}".format(k))
            break
    blendPlaylistSongs.extend(candidateSongs)

print("\nThe blend playlist has {} items".format(len(blendPlaylistSongs)))
random.shuffle(blendPlaylistSongs)
# Check to see if the blend playlist already exists for each user
random.shuffle(usersList)
for k in usersList:
    print("\nAdding {} songs to {} for {}".format(len(blendPlaylistSongs), blendPlaylistName, k.title()))
    u = users[k]
    bl = existingBlendedList(plexhost=u["host"], plextoken=u["token"], blendedListName=blendPlaylistName)
    blendedListExists = (bl["blendedListID"] != 0)
    blendedListId = bl["blendedListID"]
    if blendedListExists:
        plex.removeAllFromPlaylist(plexhost=u["host"], plextoken=u["token"], playlistid=blendedListId, verbose=verbose)
    if blendedListId == 0:
        blendedList = plex.newPlaylist(plexhost=u["host"], plextoken=u["token"], title=blendPlaylistName)
        blendedListId = blendedList["MediaContainer"]["Playlist"]["@ratingKey"]
    if blendedListId != 0:
        for songID in blendPlaylistSongs:
            plex.addItemToPlaylist(plexhost=u["host"], plextoken=u["token"], playlistId=blendedListId, itemId=songID)