"""
Created by Andrew Yeon on July 17, 2018
"""

import os
import sys
import stone
import subprocess as sp
from collections import OrderedDict
from socket import gaierror
from requests.exceptions import ConnectionError

currentErrorMess = ''
try:
    # help(yt) # documentation for youtube_dl
    currentErrorMess = '(pip install youtube_dl)'
    import youtube_dl
    currentErrorMess = '(pip install dropbox)'
    import dropbox
    currentErrorMess = "('pip install eyed3==0.8.10' and then 'pip install python-magic-bin==0.4.14')"
    import eyed3
except ImportError:
    raise Exception("Please install the following python package before proceeding, ",
          "otherwise the program will not function properly: " + currentErrorMess + "\n") from None

def printASCII():
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

'''
Clears all the text currently displayed on the terminal window and flushes the buffer
'''
def clear():
    os.system("clear")


'''
Opens file containing readable local information and returns a list containing: Dropbox API key, Dropbox destination path, 
and local destination path
''' 
def retrieveLocalInf():
    if os.path.isfile("local_inf"):
        f = open("local_inf", 'r')
        contents = f.read()
        information = contents.splitlines()
        f.close()
        print("Local_inf data found! \n")
        return information
    else:
        print("Local_inf data not found. Resuming... \nl")
        return False
 
'''
Checks all outdated python modules needed for the running of this program and updates the modules if they are outdated
'''  
def updatePackages():
    updatedPrograms = ''
    updateLog = sp.Popen(["pip list --outdated"], shell=True, stdout=sp.PIPE)
    output = updateLog.communicate()[0]
    inVenv = False
    confirm = ('y', "yes")
    deny = ('n', "no")
    # Checks if python is currently being run on a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        inVenv = True
    # CAUTION: Module is named "youtube_dl" but updateLog list names the module "youtube-dl"
    if b"youtube-dl" in output:
        if inVenv:
            while True:
                youtube_ans = input("youtube_dl is outdated and updating it is necessary to run. Would you like to update the " 
                                    "module on your virtual environment?: \n" 
                                    "(reply with 'y' to update and 'n' to quit) \n")
                youtube_ans = youtube_ans.lower()
                if youtube_ans in confirm:
                    os.system("pip install --upgrade youtube_dl")
                    updatedPrograms += "youtube-dl"
                    break
                elif youtube_ans in deny:
                    sys.exit()
                else:
                     print("Invalid answer. Please try again.")
        # (Non-virtual environment case) Might need to enter password if not admin
        else: 
            while True:
                youtube_ans = input("youtube_dl is outdated and updating it is necessary to run. Would you like to update the " 
                                    "module?: \n (Note: Admin access is required! If prompted, " 
                                    "you may need your computer's user password. \n" 
                                    "reply with 'y' to update and 'n' to quit) \n")
                if youtube_ans in confirm:
                    os.system("sudo -H pip install --upgrade youtube_dl")
                    updatedPrograms += "youtube-dl"
                    break
                elif youtube_ans in deny:
                    sys.exit()
                else:
                    print("Invalid answer. Please try again.")
    if b"dropbox" in output:
        while True:
            dropbox_ans = input("The dropbox module is outdated. Would you like to update the module?: \n" 
                                "(reply with 'y' to update and 'n' to skip) \n")
            dropbox_ans = dropbox_ans.lower()
            if dropbox_ans in confirm:
                os.system("pip install --upgrade dropbox")
                updatedPrograms += " dropbox"
                break
            elif dropbox_ans in deny:
                break
            else:
                print("Invalid answer. Please try again.")
    # Note: Don't update eyed3, doesn't function as intended after ver. 0.8.10
    return updatedPrograms

'''

'''
def createDropboxRequest(token,localInf):
    if token:
        dbx = dropbox.Dropbox(token)
        try:
            dbx.check_user()
            return dbx
        except dropbox.exceptions.AuthError:
            clear()
            print('Invalid access token was provided.')
            return None
    else:
        if localInf:
            dbx = dropbox.Dropbox(localInf[0])
            return dbx
        else:
            clear()
            print("No access token was provided. Please provide an access token to continue.")
            return None

'''

'''
def checkDropboxPath(db,path,localInf):
    if path:
        try:
            db.files_alpha_get_metadata(path)
            return path
        # Dropbox SDK currently has a dependancy issue for invalid paths. Use validation straight from stone module.
        except stone.backends.python_rsrc.stone_validators.ValidationError: 
            clear()
            print("Invalid Dropbox path was provided. Please provide an existing Dropbox directory to continue.")
            return None
    else:
        if localInf:
            return localInf[1]
        else:
            clear()
            print("No path was provided. Please provide a proper Dropbox path to continue.")
            return None
    
'''
Accepts a string containing a single block of text of  Youtube URL's and separates them into list elements
'''
def urlToList(linkString):
    # If there are any spaces, eliminate them all
    escapedString = linkString.replace('\r','\\r').replace('\n','\\n').replace('\t','\\t')
    listString = ' '.join(escapedString.split())
    print('\n LISTSTRING: ' + listString)
    strLength = len(listString)
    linkList = []
    while strLength > 0:
        firstPass = True
        currentLink = ""
        shaverIndex = 0
        # Enumerate can get both index and character?
        for character in enumerate(listString): 
            httpsSeparate = listString[character[0]:int(character[0])+6]
            httpSeparate = listString[character[0]:int(character[0])+5]
            wwwSeparate = listString[character[0]:int(character[0])+4]
            if httpsSeparate == 'https:' or httpSeparate == 'http:' or wwwSeparate == 'www.':
                if firstPass == False:
                    if wwwSeparate != 'www.':
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
Retrieves the title of a Youtube video using GET request
'''
def getTitle(url, ydl):
    infoDict = ydl.extract_info(url, download = False)
    filename = ydl.prepare_filename(infoDict)
    # removes the entire path and leaves just the filname
    separatePath = os.path.basename(filename)
    print(separatePath)
    # removes the file extension from the filename
    finalName = os.path.splitext(separatePath)[0]
    print(finalName)
    return finalName

'''

'''
def displayTitle (videoName, index, videoTotal):
    print("---------------------------------------------------------------------------------------------- \n")
    print("Downloading Youtube videos " + str(index + 1) + " out of " + str(videoTotal) + "\n",  
            "(Title: " + videoName + ") \n")
    print("---------------------------------------------------------------------------------------------- \n")

'''

'''
def replaceCharacters(charCheck):
    if '&#39;' in charCheck:
        # Apostrophe in decimal
        charCheck = charCheck.replace("&#39;","'") 
    if '&amp;' in charCheck:
        # Ampersand in decimal
        charCheck = charCheck.replace("&amp;",'&')
    if '&quot;' in charCheck:
        #Quote in decimal
        charCheck = charCheck.replace("&quot;",'"')
    if '/' in charCheck:
        charCheck = charCheck.replace('/','_')
    return charCheck
    
'''    
Passes a Youtube URL into youtube_dl and exports the video file to outDirectory
'''
# might have issues based on outDirectory 
def urlToVideo(url,outDirectory, videoCount):
    #TO DO HERE! Figuring out how to incorporate new titles based on changed metadata with youtube_dl (can change through opts?)
    ydl_opts = {'format':'bestaudio/best','outtmpl': os.path.join(outDirectory, '%(title)s.%(ext)s'), 'rejecttitle': 'True', 
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],'extractaudio' : 'True','audioformat' : 'mp3','nooverwrites': 'True', 'noplaylist': 'True'}
    # 'quiet': True # do not print messages to stdout
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            origTitle = getTitle(url[1],ydl)
            if origTitle == None:
                print("---------------------------------------------------------------------------------------------- \n")
                print(" No title was found for the given URL: \n " + url[1] + "\n",
                        "Resuming... \n")
                print("---------------------------------------------------------------------------------------------- \n")
                return False
            else:
                rmvChar = replaceCharacters(origTitle)
                artistCheck = artistFromTitle(rmvChar)
                #way to implement, get the artist name ready, download yt video as is, THEN replace the title with the new title
                displayTitle(artistCheck[0],url[0], videoCount)
                ydl.download([url[1]])
                # required for modules that require file name extensions like os, eye3d and Dropbox
                origMP3Path = os.path.join(outDirectory, origTitle + '.mp3')
                NewMP3Name = artistCheck[0] + '.mp3'
                NewMP3Path = os.path.join(outDirectory, NewMP3Name)
                os.rename(origMP3Path, NewMP3Path)
                # update the metadata of the song if artistFromTitle returns a tuple of the new song title and artist name
                if artistCheck[0] != origTitle:
                    setArtist(NewMP3Path, artistCheck[1])
                return NewMP3Name
    except youtube_dl.utils.DownloadError:
        clear()
        print("DownloadError: The video cannot be accessed. Please check the URL's or your internet connection and try again.")
        return False
    except youtube_dl.utils.UnavailableVideoError:
        clear()
        print("UnavailableVideoError: The video is currently unavailable")
        return False
    except AttributeError: 
        clear()
        print(" The Youtube URL's provided were invalid.")
        return False
    except gaierror as e:
        clear()
        raise Exception("The following connection error has been spotted. \n" + str(e) + 
                        "\n Please establish an internet connection first. \nExiting...") from None 

'''
Extracts the artist information from a given title and returns both the new song title and artist name
If none, returns a tuple of original input song name and None
'''    
def artistFromTitle(song):
    hyphenCheck = song.rfind("-")
    if hyphenCheck:
        newTitle = song[song.rfind("-") + 1:]
        newTitle = ' '.join(newTitle.split())
        noHyphens = song.replace("-"," ")
        artistExtract = noHyphens[:hyphenCheck]
        return newTitle, artistExtract
    else:
        return song, None

'''
Places the artist's name extracted from the title and places it in the song's tag instead
'''
def setArtist(songPath,artistName):
    audioFile = eyed3.load(songPath)
    audioFile.tag.artist = artistName
    audioFile.tag.save()

'''
Deletes all video, video segment, or music files in a dictionary in the current working directory
'''
def deleteItems(list):
    # Iteration over the key strings of the video dictionary
    for file in list:
        try:
            os.remove(file)
        # either the music file no longer exists or already deleted (in the case of duplicate URL's)
        except FileNotFoundError:
            pass

'''
Given a path, return True if a give path exist and False otherwise
'''
def verifyPath(path):
    if os.path.isdir(path):
        return True
    else:
        clear()
        print("Invalid path, please provide a valid path.")
        return False


'''
Main operator function that takes a list of Youtube URL's and a directory 
and downloads/converts the URL's to MP3 files into the directory
'''
def createMP3(linkList, dir):
    # Saves the current working directory
    savedCWD = os.getcwd()
    if dir != savedCWD:
        # Changes the main directory to another location
        os.chdir(dir)
    # the 0th item in the dict is updated if any of the files in linkList have a front slash in the file name
    musicList = []
    for url in enumerate(linkList):
        extractCheck = urlToVideo(url, dir, len(linkList))
        if extractCheck == False:
            currentDirectoryState = os.listdir(dir)
            toDelete = []
            for file in currentDirectoryState:
                # checks if the file being observed has the same name as the video title. Perhaps a better way to do this?
                if file in musicList:
                    toDelete.append(file)
            deleteItems(toDelete)
            return
        musicList.append(extractCheck)
    # Reverts the main directory back
    os.chdir(savedCWD)  
    return musicList

'''
Takes a Dropbox Acount Object + list of mp3 filenames + remote directory string name 
and uploads the music files to the given remote directory
'''
def uploadtoDropbox(dbxAccount, mp3Files, remoteDir):
    for music in mp3Files:
        # the last 4 indices contain the ".mp3" file extension, removed for presentation
        print("Uploading MP3: " + music[:-4])
        with open(music, 'rb') as f:
            try:
                dbxAccount.files_upload(f.read(),remoteDir + "/" +  music)
            except ConnectionError as e:
                deleteItems(mp3Files)
                clear()
                raise Exception("The following connection error has been spotted: \n \n" + str(e) + 
                             "\n \n Please establish an internet connection first. \nExiting...") from None  

def main():
    printASCII()
    
    modulesUpdated = False
    mp3ToDropbox = False
    resume = True
    createdMP3 = False
    conversionReady = False
    localInf = retrieveLocalInf()
    
    #Loop for user input on whether modules should be updated or not
    while modulesUpdated == False: 
        updateCheck = input("Would you like to check for module updates? \n"
                            "(reply with 'y' to check or 'n' to continue) \n")
        if updateCheck in ('y', "yes"):
            print("----------------------------------------------------------------------------------------------")
            print('Checking for Module Updates...')
            print("---------------------------------------------------------------------------------------------- \n")
            
            updated = updatePackages()
            if updated:
                print("\n----------------------------------------------------------------------------------------------")
                print('The following modules have been updated: ' + updated + ' \nResuming...')
                print("---------------------------------------------------------------------------------------------- \n")
                modulesUpdated = True
            else:
                print("----------------------------------------------------------------------------------------------")
                print('All modules have been accounted for! \nResuming...')
                print("---------------------------------------------------------------------------------------------- \n")
                modulesUpdated = True
        elif updateCheck in ('n', "no"):
            print("----------------------------------------------------------------------------------------------")
            print('Resuming...')
            print("---------------------------------------------------------------------------------------------- \n")
            modulesUpdated = True
        else:
            clear()
            print("No option was provided. \n")       
    # Conversion process restarts if user wishes to resume converting
    while resume == True:
        # Dropbox or Local Directory input loop
        while conversionReady == False:
            compOrDropbox = input ("Would you like to save the files to Dropbox or to a local directory?: \n" 
                                  "(reply with 'd' for Dropbox and 'l' for local directory) \n").lower()
            if compOrDropbox in ('d', "dropbox", "drop"):
                mp3ToDropbox = True
                retypeToken = True
                validDropboxDirectory = False
                dbx = False
                #Used for createMP3 method
                directory = os.getcwd()
                #Main Dropbox Path Loop. Returns here if access token is invalid
                while retypeToken == True:
                    # Dropbox API access token input loop
                    while not dbx:
                        accToken = input("\n \nPlease provide the Dropbox API access token: \n"
                                         "(Note: the token must be accurate or the files can't access your Dropbox account) \n")
                        # If the access token was invalid. Returns to beginning of Dropbox API access token input loop.
                        dbx = createDropboxRequest(accToken,localInf)
                    # Dropbox directory input loop
                    while validDropboxDirectory == False:
                        dbxDirectory = input("\n \nPlease provide the Dropbox directory where the .mp3 files will be placed in: \n"
                                        "(Note: The directory must be valid and precise. Otherwise, the program may not finish)\n")
                        pathExists = checkDropboxPath(dbx,dbxDirectory,localInf)
                        # Validation Error. The Dropbox path was invalid. Returns to beginning of Dropbox directory input loop.
                        if not pathExists:
                            pass
                        # The Dropbox directory was valid and was able to have its metadata retrieved.
                        else:
                            retypeToken = False
                            validDropboxDirectory = True   
                conversionReady = True 
            elif compOrDropbox in ('l', "local", "localdirectory", "local directory"):
                while True:
                    directory = input("\n \nPlease paste the path that you would like your music to be downloaded to: \n")
                    if directory:
                        isValid = verifyPath(directory)
                        if isValid == True:
                            break
                    else:
                        if localInf:
                            directory = localInf[2]
                            break
                        else:
                            clear()
                            print("No path was provided.") 
                conversionReady = True
            else:
                clear()
                print("Invalid Input. Please try again. \n")
        # Youtube URL to mp3 input loop
        while createdMP3 == False:
            unconvSongs = input("\n \nPlease paste the URL's of the music that is to be converted: \n")
            # Empty string was provided
            if not unconvSongs:  
                clear()
                print("No URL's were provided.")
            else:
                # Executes the conversion process and returns a dictionary with the music that was converted
                urlList = urlToList(unconvSongs)
                mp3List = createMP3(urlList,directory)
                # mp3Dict came back with no errors. Continue to Dropbox transfer, otherwise go back to Youtube URL input loop
                if mp3List:
                    createdMP3 = True
        if mp3ToDropbox:
            print("----------------------------------------------------------------------------------------------")
            print('Now Transfering files to Dropbox...')
            print("---------------------------------------------------------------------------------------------- \n")
            if not dbxDirectory:
                # If input for Dropbox directory is an empty string and local_inf exists, then set local_inf path as default Dropbox path 
                dbxDirectory = pathExists
            uploadtoDropbox(dbx, mp3List, dbxDirectory)
            print("----------------------------------------------------------------------------------------------")
            print('Now Deleting MP3 Files Locally...')
            print("---------------------------------------------------------------------------------------------- \n")    
            deleteItems(mp3List)
        print("----------------------------------------------------------------------------------------------")
        print('Finished!')
        print("---------------------------------------------------------------------------------------------- \n")

        # Continue MP3 Creation input Loop
        while True:
            resumeResponse = input("Would you like to resume converting Youtube Videos?: \n"
                           "(reply with 'y' to continue and 'n' to quit)\n")
            resumeResponse = resumeResponse.lower()
            if resumeResponse in ('y', "yes"):
                mp3ToDropbox = False
                createdMP3 = False
                conversionReady = False
                break
            elif resumeResponse in ('n', "no"):
                resume = False
                break
            else:
                clear()
                print("No option was provided.")

main()
