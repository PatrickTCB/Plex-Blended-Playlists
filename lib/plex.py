import requests
import xmltodict
import curlify

def getMachineIdentifier(plexhost, plextoken) -> dict:
    machineResult = requests.get("{}/identity/?X-Plex-Token={}".format(plexhost, plextoken))
    plexDict = xmltodict.parse(machineResult.text)
    return plexDict["MediaContainer"]["@machineIdentifier"]

def getAllPlaylists(plexhost, plextoken) -> dict:
    path = "playlists?playlistType=audio&includeCollections=1&includeExternalMedia=1&includeAdvanced=1&includeMeta=1&X-Plex-Token={}".format(plextoken)
    r = requests.get("{}/{}".format(plexhost, path))
    if r.status_code == 200:
        return xmltodict.parse(r.text)
    else:
        print("Error getting playlist info\nStatus: {}\n{}".format(r.status_code, r.text))
        print(curlify.to_curl(r.request))
        return {}

def getSinglePlaylist(plexhost, plextoken, playlistid) -> dict:
    r = requests.get("{}/playlists/{}/items?X-Plex-Token={}".format(plexhost,  playlistid, plextoken))
    if r.status_code == 200:
        plexDict = xmltodict.parse(r.text)
        return plexDict
    else:
        print("Couldn't get playlist id {}\nStatus: {}\n{}".format(playlistid, r.status_code, r.text))
        print(curlify.to_curl(r.request))
        return {}

def newPlaylist(plexhost, plextoken, title) -> dict:
    machineId = getMachineIdentifier(plexhost, plextoken)
    path = "playlists?type=audio&title={}&smart=0&uri=server://{}/com.plexapp.plugins.library&X-Plex-Token={}".format(title, machineId, plextoken)
    r = requests.post("{}/{}".format(plexhost, path))
    if r.status_code == 200:
        return xmltodict.parse(r.text)
    else:
        print("Error creating playlist\nStatus: {}\n{}".format(r.status_code, r.text))
        print(curlify.to_curl(r.request))
        return {}

def removeFromPlaylist(plexhost, plextoken, playlistid, playlistitem) -> dict:
    r = requests.delete("{}/playlists/{}/items/{}?X-Plex-Token={}".format(plexhost, playlistid, playlistitem, plextoken))
    if r.status_code == 200:
        plexDict = xmltodict.parse(r.text)
        return plexDict
    else:
        print("Couldn't delete item '{}' from playlist '{}'\nStatus: {}\n".format(playlistitem, playlistid, r.status_code, r.text))
        print(curlify.to_curl(r.request))
        return {}

def removeAllFromPlaylist(plexhost, plextoken, playlistid, verbose):
    pList = getSinglePlaylist(plexhost, plextoken, playlistid)
    tracksToRemoveFromList = []
    if "Track" in pList["MediaContainer"].keys():
        if isinstance(pList["MediaContainer"]["Track"], list):
            tracksToRemoveFromList = pList["MediaContainer"]["Track"]
        if isinstance(pList["MediaContainer"]["Track"], dict):
            tracksToRemoveFromList.append(pList["MediaContainer"]["Track"])
    for track in tracksToRemoveFromList:
        if verbose:
            print("Removing '{}' from '{}'".format(track["@title"], pList["@title"]))
        removeFromPlaylist(plexhost, plextoken, playlistid, playlistitem=track["@playlistItemID"])

def addItemToPlaylist(plexhost, plextoken, playlistId, itemId) -> dict:
    machineId = getMachineIdentifier(plexhost, plextoken)
    plexURL = "{}/playlists/{}/items?uri=server://{}/com.plexapp.plugins.library/library/metadata/{}&X-Plex-Token={}".format(plexhost, playlistId, machineId, itemId, plextoken)
    addItemResult = requests.put(plexURL)
    plexDict = xmltodict.parse(addItemResult.text)
    plexDict["itemAdded"] = (plexDict["MediaContainer"]["@leafCountAdded"] == "1")
    plexDict["url"] = plexURL
    plexDict["curl"] = curlify.to_curl(addItemResult.request)
    return plexDict