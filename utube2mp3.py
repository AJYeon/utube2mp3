"""
Created by Andrew Yeon on July 17, 2018
"""

import urllib.request
import os
import sys
import subprocess as sp
from collections import OrderedDict



try:
    import youtube_dl  # pip install youtube_dl
except ImportError:
    print("""Please install the youtube_dl python package before proceeding, 
             otherwise the program will not function properly (pip install youtube_dl) \n""")
    sys.exit()
try:
    import dropbox  # pip install dropbox
except ImportError:
    print("""Please install the dropbox python package before proceeding, 
           otherwise the program will not function properly  (pip install dropbox) \n""")
    sys.exit()
try:
    from ffmpy import FFmpeg  # pip install ffmpy + brew install FFmpeg
except ImportError:
    print("""Please install the ffmpy python package from brew before proceeding, 
           otherwise the program will not function properly  [(pip install ffmpy) + (brew install FFmpeg)] \n""")
    sys.exit()

try:
    import eyed3  # pip install eyeD3 + pip install python-magic-bin==0.4.14
except ImportError:
    print("""Please install the eyeD3 python package before proceeding, 
           otherwise the program will not function properly (pip install eyeD3 + pip install python-magic-bin==0.4.14) \n""")
    sys.exit()


'''
Clears all the text currently displayed on the terminal window and flushes the buffer
'''
def clear():
    os.system("clear")

'''
Checks all outdated python modules needed for the running of this program and updates the modules if they are outdated
'''  
def updatePackages():
    updatedPrograms = ''
    updateLog = sp.Popen(["pip list --outdated"], shell=True, stdout=sp.PIPE)
    output = updateLog.communicate()[0]
    if b'youtube-dl' in output:  # CAUTION: "youtube-dl" is named in the updateLog list but package is named "youtube_dl"
        print("----------------------------------------------------------------------------------------------")
        print('Admin access required! Please enter your password')
        print("---------------------------------------------------------------------------------------------- \n")
        os.system('sudo -H pip install --upgrade youtube_dl')  # Might need to enter password if not admin
        updatedPrograms += "youtube-dl"
    if b'dropbox' in output:
        os.system('pip install --upgrade dropbox')
        updatedPrograms += " dropbox"
    if b'ffmpy' in output:
        os.system('pip install --upgrade ffmpy')
        updatedPrograms += " ffmpy"
    return updatedPrograms
    
'''
Accepts a string containing a single block of text of  Youtube URL's and separates them into list elements
'''
def urlToList(linkString):
    listString = ' '.join(linkString.split()) # If there are any spaces, eliminate them all
    strLength = len(listString)
    linkList = []
    while strLength > 0:
        firstPass = True
        currentLink = ""
        shaverIndex = 0
        for character in enumerate(listString):  # Enumerate can get both index and character?
            if listString[character[0]:int(character[0])+6] == 'https:':
                if firstPass == False:
                    break
                else:
                    firstPass = False
            currentLink += character[1]
            shaverIndex += 1
        linkList.append(currentLink)
        listString = listString[shaverIndex:]
        strLength = len(listString) 
    return linkList


'''
Calls a GET request on a given URL. Helper function to getTitle
'''
def requestGET(url): 
    try:
        headers = {}
        headers['User-Agent'] =  "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib.request.Request(url, headers = headers)
        resp = urllib.request.urlopen(req)
        respData = resp.read()
        return respData
    except Exception as e:
        print(str(e))

'''        
Retrieves the title of a Youtube video using GET request
'''
def getTitle(url):
    strData = requestGET(url).decode()  # Converts Bytes-like Object into a decoded string
    titleTag = "<title>"
    endOfTitle = "- YouTube"
    titleStartIndex = strData.find(titleTag) +7
    titleEndIndex = strData.find(endOfTitle) -1
    videoTitle = strData[titleStartIndex : titleEndIndex]
    if len(videoTitle) > 100:  # The video doesn't have a proper title; Exceeded Youtube's 100 character limit
        videoTitle = "N/A"
    return videoTitle

'''    
Passes a Youtube URL into youtube_dl and exports the video file to outDirectory
'''
def urlToVideo(url,outDirectory):
    ydl_opts = {'outtmpl': outDirectory}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError:
            clear()
            print("DownloadError: The video cannot be accessed.")
            return False
        except youtube_dl.utils.UnavailableVideoError:
            clear()
            print("UnavailableVideoError: The video is currently unavailable")
            return False
    
'''      
Relocates video files with titles including '/' mistakenly parsed as an additional directory to the root directory 
and returns a string of the relocated filepath. Helper function to getFFmpegDicts
'''
def movetoRoot(mainDir,dirCheck):
    if os.path.isdir(dirCheck):
        #tempDir = mainDir + '/' + dirCheck
        tempDir = os.path.join(mainDir, dirCheck)
        remDirectory = os.listdir(tempDir)
        for file in remDirectory:
            #newFileName = dirCheck + '/' + file
            newFileName = os.path.join(dirCheck, file)
            tempPath = os.path.join(tempDir, file)
            rootPath = os.path.join(mainDir, file)
            os.rename(tempPath, rootPath)
        os.rmdir(tempDir)
        #print("newFileName: " + newFileName)
        return newFileName

'''      
Accepts a directory of video files and returns boilerplate dictionaries of the files for FFmpeg to properly parse
'''
def getFFmpegDicts(dir,frontSlashTitles):
    vidDict = {}
    mp3Dict = {}
    if frontSlashTitles:
        if sys.platform not in ('win32', 'cygwin'):
            for file in frontSlashTitles:
                fileCheck = movetoRoot(dir, file[:file.rfind('/')])
                oldPath = os.path.join(dir, fileCheck[fileCheck.rfind('/') + 1:])
                underscorePath =  os.path.join(dir, fileCheck.replace('/','_'))
                os.rename(oldPath, underscorePath)
                # Backslashes replaced with underscores. Possible to reapply the backslashes?
    musicDirectory = os.listdir(dir)
    vidList = []
    mp3List = []
    artList = []
    isArtist = True
    mapAccum = 0
    for file in musicDirectory:
        #if file.endswith('.mkv') or file.endswith('.mp4') or file.endswith('.ogg') or file.endswith('.webm') or file.endswith('.flv'):
        if file.endswith((".mkv", ".mp4", ".ogg", ".webm", ".flv")):
            artCheck = file.rfind("-")
            if artCheck == -1:
                isArtist = False
            if isArtist == True:
                newTitle = file[file.rfind("-") + 1:]
                newTitle = ' '.join(newTitle.split())
                noHyphens = file.replace("-"," ")
                artList.append(noHyphens[:artCheck])
            else:
                newTitle = file
                artList.append("")
            os.rename(os.path.join(dir, file), os.path.join(dir, newTitle))
            vidList.append((newTitle, None))
            mp3String = newTitle[:newTitle.rfind('.')] + '.mp3'  # indexes the file extension of the video and replaces everything after and including the '.' with '.mp3'
            mp3List.append((mp3String,"-map " + str(mapAccum) + ":1")) # additional parameters on top the mp3 file name
            mapAccum += 1
    vidDict = OrderedDict(vidList)  # Because Dictionaries stores keys and values in abritrary order, OrderedDict remembers the order saved 
    mp3Dict = OrderedDict(mp3List)  
    return(vidDict,mp3Dict,artList)



'''
Runs FFmpeg on the given dictionary of video files and creates music files with the given output dictionary
'''
def videosToMp3(inputDict, outputDict):
    ff = FFmpeg(inputs = inputDict , outputs = outputDict)
    ff.cmd
    ff.run()
    
'''
Removes the artist's name from the title and places it in the song's tag instead
'''
def setArtist(path,metadata,songs):
    index = 0
    #print(songs)
    for entry in songs.items():
        songPath = os.path.join(path, entry[0])
        #audiofile =  eyed3.load(path + '/' + entry[0])
        audioFile = eyed3.load(songPath)
        audioFile.tag.artist = metadata[index]
        audioFile.tag.save()
        index += 1

'''
Deletes all video files in a dictionary in the current working directory
'''
def deleteVideos(Dict):
    for videos in Dict.items():  # Iteration over the key strings of the video dictionary
        os.remove(videos[0])

'''
Deletes all music files in a dictionary in the current working directory
'''
def deleteMusic(Dict):
    for mp3 in Dict.items(): 
        os.remove(mp3[0])

'''
Main operator function that takes a list of Youtube URL's and a directory and downloads/converts the URL's to MP3 files into the directory
'''
def createMP3(linkList, dir):
    savedCWD = os.getcwd()  # Saves the current working directory
    if dir != savedCWD:
        os.chdir(dir)  # Changes the main directory to another location
    frontSlashList = []
    for url in enumerate(linkList):
        videoName = getTitle(url[1])
        if '&#39;' in videoName:
            videoName = videoName.replace('&#39;',"'")  # Apostrophe in decimal
        if '&amp;' in videoName:
            videoName = videoName.replace('&amp;','&')  # Ampersand in decimal
        if '/' in videoName:
             frontSlashList.append(videoName)
             
        print("---------------------------------------------------------------------------------------------- \n")
        print("Downloading Youtube videos " + str(url[0] + 1) + " out of " + str(len(linkList)) + "\n  (Title: " + videoName + ") \n")
        print("---------------------------------------------------------------------------------------------- \n")
        
        #videoDirectory = dir + '/' + videoName
        videoDirectory = os.path.join(dir, videoName)
        print("videoDirectory: " + videoDirectory)
        extractCheck = urlToVideo(url[1],videoDirectory)
        if extractCheck == False:
            return
    videoDict,musicDict,artistList = getFFmpegDicts(dir,frontSlashList)
    
    print("---------------------------------------------------------------------------------------------- ")
    print('Now Converting videos to MP3...')
    print("---------------------------------------------------------------------------------------------- \n")
    
    videosToMp3(videoDict,musicDict)

    print("---------------------------------------------------------------------------------------------- ")
    print('Now Modifying MP3 Metadata...')
    print("---------------------------------------------------------------------------------------------- \n")
    
    setArtist(dir,artistList,musicDict)
    
    print("----------------------------------------------------------------------------------------------")
    print("Now Deleting Videos...")
    print("---------------------------------------------------------------------------------------------- \n")
    
    deleteVideos(videoDict)            
    os.chdir(savedCWD)  # Reverts the main directory back
    return musicDict


def main():
    print("----------------------------------------------------------------------------------------------")
    print("  _      _  ________  _      _  ________  ________   ______   __       __  _______   ________ ")   
    print(" | |    | ||__    __|| |    | ||   __   ||        | /  _   \ |  \     /  ||  ____ \ |_____   |")
    print(" | |    | |   |  |   | |    | || |____|_||  ______||__/ /  | |   \   /   || |____| |     /  / ")
    print(" | |    | |   |  |   | |    | ||      <_ | |______     /  /  |    \_/    ||   ____/     /  /  ")
    print(" | |    | |   |  |   | |    | ||  ____  ||  ______|   /  /   |  |\   /|  ||  |         |_  \  ")
    print(" | |    | |   |  |   | |    | || |    | || |______   /  /    |  | \_/ |  ||  |           \  \ ")
    print(" | \____/ |   |  |   | \____/ || |____| ||        | /  /____ |  |     |  ||  |      /\____)  )")
    print("  \______/    [__]    \______/ [________]|________||________||__|     |__||__|      \_______/ ")
    print("---------------------------------------------------------------------------------------------- \n \n")
    mp3ToDropbox = False
    resume = True
    
    print("----------------------------------------------------------------------------------------------")
    print('Checking for Module Updates...')
    print("---------------------------------------------------------------------------------------------- \n")
    
    updated = updatePackages()
    if updated:
        
        print("\n----------------------------------------------------------------------------------------------")
        print('Outdated modules have been found: ' + updated + ' \n Modules have been Updated! Resuming...')
        print("---------------------------------------------------------------------------------------------- \n")
        
    else:
        
        print("----------------------------------------------------------------------------------------------")
        print('All modules are currently up-to-date! Resuming...')
        print("---------------------------------------------------------------------------------------------- \n")
        
    while resume == True:  # Conversion process restarts if user wishes to resume converting
        while True:
            clear()
            compOrDropbox = input("Would you like to save the files to Dropbox or to a local directory?: \n (reply with 'd' for Dropbox and 'l' for local directory) \n")
            #if compOrDropbox == 'd' or  compOrDropbox == 'D' or compOrDropbox == 'Dropbox' or compOrDropbox == 'dropbox' or  compOrDropbox == 'drop' or  compOrDropbox == 'Drop':
            if compOrDropbox in ('d', 'D', 'Dropbox', 'dropbox', 'drop', 'Drop'):
                mp3ToDropbox = True
                directory = os.getcwd()
                while True:
                    accToken = input("\n \n Please provide the access token given by the Dropbox API allowing access to the files: \n (Note: the token must be accurate or the file won't show up on your Dropbox account) \n")  # No Error Catching on access token
                    if accToken:
                        try:
                            dbx = dropbox.Dropbox(accToken)
                        except (rest.ErrorResponse, e):
                            clear()
                            print('Error: %s' % (e,))
                        else:
                            break  
                    else:
                        dbx = dropbox.Dropbox('sjUdCDDblF8AAAAAAAAA6N5N2Ou2UdMxXrSZDb8PZmegtCelLbr3I6csg7myrvW5')
                        break
                dbxDirectory = input("\n \n Please provide the directory in Dropbox to which the .mp3 files will be placed in: \n")
                if not dbxDirectory:
                    dbxDirectory = "/Public/Music Folder"
                    break
            #elif compOrDropbox == 'l' or compOrDropbox == 'local' or compOrDropbox == 'localdirectory' or compOrDropbox == 'local directory' or compOrDropbox == 'Local' or compOrDropbox == 'Localdirectory' or compOrDropbox == 'Local directory' or compOrDropbox == 'Local Directory':
            elif compOrDropbox in ('l', "local", "localdirectory", "local directory", "Local", "Localdirectory", "LocalDirectory", "Local Directory"):
                while True:
                    directory = input("\n \n Please paste the path that you would like your music to be downloaded to: \n")
                    if directory:
                        if os.path.isdir(directory):
                            break
                        else:
                            clear()
                            print("Invalid path, please provide a valid path.")
                    else:
                        directory = "/Users/andrewyeon/Documents/Music Folder"
                        break
                break
            else:
                clear()
                print("Invalid Input. Please try again. \n")
        while True:
            unconvSongs = input("\n \n Please paste the URL's of the music that is to be converted: \n")
            mp3Dict = []
            if not unconvSongs:  # Empty string was provided
                clear()
                print("No URL's were provided.")
            else:
                try:
                    mp3Dict = createMP3(urlToList(unconvSongs),directory) # Executes the conversion process and returns a dictionary with the music that was converted
                except AttributeError or not mp3Dict: # Error in parsing youtube URLs or one of the URL's were either unavailable or stricken with copyright grounds
                    clear()
                    print(" The Youtube URL's provided were invalid.")
                else:
                    break
        if mp3ToDropbox:
            print("----------------------------------------------------------------------------------------------")
            print('Now Transfering files to Dropbox...')
            print("---------------------------------------------------------------------------------------------- \n")
            try:
                for music in mp3Dict.items():
                    print("Uploading MP3: " + music[0][:-4])
                    with open(music[0], 'rb') as f:
                        dbx.files_upload(f.read(),dbxDirectory + "/" +  music[0])
            except dropbox.stone_validators.ValidationError:
                print("Invalid Dropbox path. Please restart the script to try again.")
            except dropbox.exceptions.ApiError:
                print("Duplicate MP3 files found in Dropbox file. If undesired, please delete the mp3 files, restart the script, and try again.")
            print("----------------------------------------------------------------------------------------------")
            print('Now Deleting MP3 Files Locally...')
            print("---------------------------------------------------------------------------------------------- \n")    
            deleteMusic(mp3Dict)
        print("----------------------------------------------------------------------------------------------")
        print('Finished!')
        print("---------------------------------------------------------------------------------------------- \n")

        while True:
            resume = input("Would you like to resume converting Youtube Videos?: \n(reply with 'y' to continue and 'n' to quit)\n")
            if resume in ('y', "yes", 'Y', "Yes", "YES"):
                mp3ToDropbox = False
                resume = True
                break
            elif resume in ('n', "no", 'N', "No", "NO"):
                mp3ToDropbox = False
                resume = False
                break
            else:
                clear()
                print("No option was provided.")

main()
