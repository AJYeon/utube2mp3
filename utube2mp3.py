"""
Created by Andrew Yeon on July 17, 2018
"""

import urllib
import os
import sys
import subprocess as sp
from collections import OrderedDict
from socket import gaierror

currentErrorMess = ''
try:
    # help(yt) # documentation for youtube_dl
    currentErrorMess = '(pip install youtube_dl)'
    import youtube_dl
    currentErrorMess = '(pip install dropbox)'
    import dropbox
    currentErrorMess = "('brew install FFmpeg' and then 'pip install ffmpy')"
    from ffmpy import FFmpeg
    currentErrorMess = "('pip install eyed3==0.8.10' and then 'pip install python-magic-bin==0.4.14')"
    import eyed3
except ImportError:
    raise Exception("Please install the following python package before proceeding, ",
          "otherwise the program will not function properly: " + currentErrorMess + "\n") from None


'''
Clears all the text currently displayed on the terminal window and flushes the buffer
'''
def clear():
    os.system("clear")

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
Calls a GET request on a given URL. Helper function to getTitle and checkInternetConnection
'''
def requestGET(url): 
    try:
        user = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        headers = {}
        headers['User-Agent'] = user
        req = urllib.request.Request(url, headers = headers)
        resp = urllib.request.urlopen(req)
        respData = resp.read()
        return respData
    # the 'from None' lines eliminate duplication of 'another exception occurred' lines, cleaning up output 
    except gaierror as e:
        clear()
        raise Exception("The following connection error has been spotted. \n" + str(e) + 
                        "\n Please establish an internet connection first. \nExiting...") from None 
    except urllib.error.URLError as e:
        clear()
        raise Exception("The following connection error has been spotted. \n" + str(e) + 
                        "\n Please establish an internet connection first. \nExiting...") from None

'''
Calls requestGET with some test URL to check internet connectivity. Error-catching helper function.
'''
def checkInternetConnection():
    testURL = 'https://pypi.org/simple'
    #requestGET will handle any internet connectivity issues, returning here means connection was established
    requestGET(testURL) 

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
    checkInternetConnection()
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
    if b"ffmpy" in output:
        while True:
            ffmpy_ans = input("The ffmpy module is outdated. Would you like to update the module?: \n" 
                              "(reply with 'y' to update and 'n' to skip) \n")
            ffmpy_ans = ffmpy_ans.lower()
            if ffmpy_ans in confirm:
                os.system("pip install --upgrade ffmpy")
                updatedPrograms += " ffmpy"
                break
            elif ffmpy_ans in deny:
                break
            else:
                print("Invalid answer. Please try again.")
    # Note: Don't update eyed3, doesn't function as intended after ver. 0.8.10
    return updatedPrograms

def createDropboxRequest(token,localInf):
    if token:
        dbx = dropbox.Dropbox(token)
        return dbx
    else:
        if localInf:
            dbx = dropbox.Dropbox(localInf[0])
            return dbx
        else:
            clear()
            print("No access token was provided. Please provide an access token to continue.")
            return None

def checkDropboxPath(db,path,localInf):
    checkInternetConnection()
    if path:
        try:
            db.files_alpha_get_metadata(path)
            return path
        except dropbox.stone_validators.ValidationError:
            clear()
            print("Invalid Dropbox path was provided. Please provide an existing Dropbox directory to continue.")
            valError = "VE"
            return valError
        except dropbox.exceptions.AuthError:
            clear()
            print("Invalid access token was provided. Please provide a proper access token to continue.")
            badATError = "AUT"
            return badATError
        except dropbox.exceptions.BadInputError:
            clear()
            print("Invalid access token was provided. Please provide a proper access token to continue.")
            badInError = "BIE"
            return badInError
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
Retrieves the title of a Youtube video using GET request
'''
def getTitle(url):
    # Converts Bytes-like Object into a decoded string
    strData = requestGET(url).decode()
    titleTag = "<title>"
    endOfTitle = "- YouTube"
    titleStartIndex = strData.find(titleTag) +7
    titleEndIndex = strData.find(endOfTitle) -1
    videoTitle = strData[titleStartIndex : titleEndIndex]
    # The video doesn't have a proper title; Exceeded Youtube's 100 character limit
    if len(videoTitle) > 100: 
        videoTitle = "N/A"
    return videoTitle

'''    
Passes a Youtube URL into youtube_dl and exports the video file to outDirectory
'''
def urlToVideo(url,outDirectory):
    checkInternetConnection()
    ydl_opts = {'outtmpl': outDirectory, 'rejecttitle': 'True', 'nooverwrites': 'True', 'noplaylist': 'True'}
    # 'quiet': True # do not print messages to stdout
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
        except AttributeError: 
            clear()
            print(" The Youtube URL's provided were invalid.")
            return False
    
'''      
Relocates video files with titles including '/' mistakenly parsed as an additional directory to the root directory 
and returns a string of the relocated filepath. Helper function to getFFmpegDicts
'''
def movetoRoot(mainDir,dirCheck):
    if os.path.isdir(dirCheck):
        tempDir = os.path.join(mainDir, dirCheck)
        remDirectory = os.listdir(tempDir)
        for file in remDirectory:
            newFileName = os.path.join(dirCheck, file)
            tempPath = os.path.join(tempDir, file)
            rootPath = os.path.join(mainDir, file)
            # os.rename moves the file from one directory to another
            os.rename(tempPath, rootPath)
        os.rmdir(tempDir)
        return newFileName

'''      
Accepts a directory of video files and returns boilerplate dictionaries of the files for FFmpeg to properly parse
'''
def getFFmpegDicts(dir,frontSlashTitles):
    vidDict = {}
    mp3Dict = {}
    print(frontSlashTitles)
    if frontSlashTitles['FSFileExists'] == True:
        if sys.platform not in ("win32", "win64", "cygwin"):
            for file in frontSlashTitles:
                #Title had front flash in it
                if frontSlashTitles[file] == True and file != 'FSFileExists':
                    fileCheck = movetoRoot(dir, file[:file.rfind('/')])
                    oldPath = os.path.join(dir, fileCheck[fileCheck.rfind('/') + 1:])
                    # Titles with backslashes replaced with underscores. Possible to reapply the backslashes?
                    underscorePath =  os.path.join(dir, fileCheck.replace('/','_'))
                    os.rename(oldPath, underscorePath)
    musicDirectory = os.listdir(dir)
    vidList = []
    mp3List = []
    artList = []
    isArtist = True
    mapAccum = 0
    for file in musicDirectory:
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
            # indexes the file extension of the video and replaces everything after and including the '.' with '.mp3'
            mp3String = newTitle[:newTitle.rfind('.')] + '.mp3'
            # additional parameters on top the mp3 file name
            mp3List.append((mp3String,"-map " + str(mapAccum) + ":1"))
            mapAccum += 1
    # Because Dictionaries stores keys and values in abritrary order, OrderedDict remembers the order saved
    vidDict = OrderedDict(vidList) 
    mp3Dict = OrderedDict(mp3List)  
    return(vidDict,mp3Dict,artList)



'''
Runs FFmpeg on the given dictionary of video files and creates music files with the given output dictionary
'''
def videosToMp3(inputDict, outputDict):
    ff = FFmpeg(inputs = inputDict , outputs = outputDict, global_options='-y') 
    # -n (global option): Do not overwrite output files, and exit immediately if a specified output file already exists
    ff.cmd
    ff.run()
    
'''
Removes the artist's name from the title and places it in the song's tag instead
'''
def setArtist(path,metadata,songs):
    index = 0
    for entry in songs.items():
        songPath = os.path.join(path, entry[0])
        audioFile = eyed3.load(songPath)
        audioFile.tag.artist = metadata[index]
        audioFile.tag.save()
        index += 1

'''
Deletes all video, video segment, or music files in a dictionary in the current working directory
'''
def deleteItems(dict):
    # Iteration over the key strings of the video dictionary
    for file in dict.items():
        os.remove(file[0])


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
    frontSlashDict = {'FSFileExists': False}
    for url in enumerate(linkList):
        videoName = getTitle(url[1])
        if '&#39;' in videoName:
            # Apostrophe in decimal
            videoName = videoName.replace("&#39;","'") 
        if '&amp;' in videoName:
            # Ampersand in decimal
            videoName = videoName.replace("&amp;",'&')
        if '&quot;' in videoName:
            # Ampersand in decimal
            videoName = videoName.replace("&quot;",'"')
        if '/' in videoName:
            frontSlashDict['FSFileExists'] = True
            frontSlashDict[videoName] = True
        else:
            frontSlashDict[videoName] = False
        print("---------------------------------------------------------------------------------------------- \n")
        print("Downloading Youtube videos " + str(url[0] + 1) + " out of " + str(len(linkList)) + "\n",  
              "(Title: " + videoName + ") \n")
        print("---------------------------------------------------------------------------------------------- \n")
        videoDirectory = os.path.join(dir, videoName)
        print("videoDirectory: " + videoDirectory)
        extractCheck = urlToVideo(url[1],videoDirectory)
        if extractCheck == False:
            currentDirectoryState = os.listdir(dir)
            toDelete = []
            for file in currentDirectoryState:
                # checks if the file being observed has the same name as the video title.
                # Excluding the FSFileExists Boolean. If so, prepare to delete it.
                if file.startswith(tuple(frontSlashDict.keys())[1:]):
                    toDelete.append(file)
            deleteItems(toDelete)
            return
    videoDict,musicDict,artistList = getFFmpegDicts(dir,frontSlashDict)
    
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
    
    deleteItems(videoDict)
    # Reverts the main directory back
    os.chdir(savedCWD)  
    return musicDict

'''
Takes a Dropbox Acount Object + dictionary of mp3 filenames + remote directory string name 
and uploads the music files to the given remote directory
'''
def uploadtoDropbox(dbxAccount, mp3Files, remoteDir):
    # passing mp3Files as a value so that it's not passed as a reference (change outside values)
    mp3Files = mp3Files
    # list of finished files that can be ignored for continued uploads in the case of APIError
    finishedUploads = []
    uploadFinished = False
    while uploadFinished != True:
        try:
            for music in mp3Files.items():
                # the last 4 indices contain the ".mp3" file extension, removed for presentation
                print("Uploading MP3: " + music[0][:-4])
                with open(music[0], 'rb') as f:
                    dbxAccount.files_upload(f.read(),remoteDir + "/" +  music[0])
                finishedUploads.append(music)
            uploadFinished = True
        except dropbox.exceptions.ApiError:
            for filename in finishedUploads:
                del mp3Files[filename]
            print("Duplicate MP3 files found in Dropbox for the following file: " + music, 
                    "\n Uploading remaining files. If undesired, please stop, handle the duplicate, and try again.")


def main():
    printASCII()
    
    mp3ToDropbox = False
    resume = True
    modulesUpdated = False
    createdMP3 = False
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
        while True:
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
                        dbx = createDropboxRequest(accToken,localInf)
                    retypeToken = False
                    # Dropbox directory input loop
                    while validDropboxDirectory == False:
                        dbxDirectory = input("\n \nPlease provide the Dropbox directory where the .mp3 files will be placed in: \n"
                                        "(Note: The directory must be valid and precise. Otherwise, the program may not finish)\n")
                        pathExists = checkDropboxPath(dbx,dbxDirectory,localInf)
                        # Validation Error. The Dropbox path was invalid. Returns to beginning of Dropbox directory input loop.
                        if pathExists == "VE":
                            pass
                        # Bad Input Error. The access token was invalid. Returns to beginning of Main Dropbox Path loop.
                        elif pathExists == "BIE" or pathExists == "AUT":
                            retypeToken = True
                            validDropboxDirectory = True
                        # The Dropbox directory was valid and was able to have its metadata retrieved.
                        else:
                            validDropboxDirectory = True   
                break 
            elif compOrDropbox in ('l', "local", "localdirectory", "local directory"):
                while True:
                    directory = input("\n \nPlease paste the path that you would like your music to be downloaded to: \n")
                    if directory:
                        if os.path.isdir(directory):
                            break
                        else:
                            clear()
                            print("Invalid path, please provide a valid path.")
                    else:
                        if localInf:
                            directory = localInf[2]
                            break
                        else:
                            clear()
                            print("No path was provided.") 
                break
            else:
                clear()
                print("Invalid Input. Please try again. \n")
        # Youtube URL to mp3 input loop
        while createdMP3 == False:
            unconvSongs = input("\n \nPlease paste the URL's of the music that is to be converted: \n")
            mp3Dict = []
            # Empty string was provided
            if not unconvSongs:  
                clear()
                print("No URL's were provided.")
            else:
                # Executes the conversion process and returns a dictionary with the music that was converted
                mp3Dict = createMP3(urlToList(unconvSongs),directory)
                # mp3Dict came back with no errors. Continue to Dropbox transfer portion
                if mp3Dict:
                    createdMP3 = True
                else:
                    # CreateMP3 returns with no value due to some Youtube URL error. Goes back to Youtube URL input loop
                    clear()
                    print(" The Youtube URL's provided were invalid.")
        if mp3ToDropbox and mp3Dict != None:
            print("----------------------------------------------------------------------------------------------")
            print('Now Transfering files to Dropbox...')
            print("---------------------------------------------------------------------------------------------- \n")
            checkInternetConnection()
            if not dbxDirectory:
                # If input for Dropbox directory is an empty string and local_inf exists, then set local_inf path as default Dropbox path 
                dbxDirectory = pathExists
            uploadtoDropbox(dbx, mp3Dict, dbxDirectory)
            print("----------------------------------------------------------------------------------------------")
            print('Now Deleting MP3 Files Locally...')
            print("---------------------------------------------------------------------------------------------- \n")    
            deleteItems(mp3Dict)
        print("----------------------------------------------------------------------------------------------")
        print('Finished!')
        print("---------------------------------------------------------------------------------------------- \n")

        while True:
            resume = input("Would you like to resume converting Youtube Videos?: \n"
                           "(reply with 'y' to continue and 'n' to quit)\n")
            resume = resume.lower()
            if resume in ('y', "yes"):
                mp3ToDropbox = False
                resume = True
                break
            elif resume in ('n', "no"):
                mp3ToDropbox = False
                resume = False
                break
            else:
                clear()
                print("No option was provided.")

main()
