"""Created by Andrew Yeon on July 17, 2018."""
"""
use yt_dlp over youtube_dl for now:
 https://stackoverflow.com/questions/75495800/error-unable-to-extract-uploader-id-youtube-discord-py
 
install ffmpeg for replit:
https://dev.to/mrbotdeveloper/installing-ffmpeg-in-replit-43g1

add ffmpeg into nix file:
https://ask.replit.com/t/code-cannot-locate-ffmpeg-file-followed-the-instructions/35377


replace Dropbox API with Google API:
https://www.thepythoncode.com/article/using-google-drive--api-in-python
delete when done:
https://www.dropbox.com/developers/apps/info/z6jry1h8f6ool9w#settings

FOR FIRST RUN, to authentic the pickle file, RUN IN LOCAL IDE, NOT REPLIT
make sure to publish to production in API & Services\OAuth consent screen when starting 

# use this as reference when splitting file into multiple modules:
https://github.com/NeuralNine/youtube-downloader-converter/blob/master/file_converter.py
"""

import os
import sys
import re
import subprocess as sp
import pickle
from socket import gaierror
from typing import Type

from requests.exceptions import ConnectionError
import stone


current_error_mess = ''
try:
    current_error_mess = '(pip install youtube_dl)'
    #import youtube_dl
    import yt_dlp as youtube_dl
    current_error_mess = "'(pip install google-api-python-client' and then pip install google-auth-httplib2)'"
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import UnknownApiNameOrVersion, HttpError
    from google.auth.transport.requests import Request
    current_error_mess = '(pip install google-auth-oauthlib)'
    from google_auth_oauthlib.flow import InstalledAppFlow
    current_error_mess = "('pip install eyed3==0.8.10' and then 'pip install python-magic-bin==0.4.14')"
    import eyed3
except ImportError:
    raise Exception("Please install the following python package before",
                    "proceeding, otherwise the program will not function",
                    "properly: " + current_error_mess + "\n") from None


def print_ASCII():
    print("----------------------------------------------------------------"
          "------------------------------")
    print("  _      _  ________  _      _  ________  ________   ______   __"
          "       __  _______   ________ ")
    print(" | |    | ||__    __|| |    | ||   __   ||        | /  _   \ |  "
          "\     /  ||  ____ \ |_____   |")
    print(" | |    | |   |  |   | |    | || |____|_||  ______||__/ /  | |  "
          " \   /   || |____| |     /  / ")
    print(" | |    | |   |  |   | |    | ||      <_ | |______     /  /  |  "
          "  \_/    ||   ____/     /  /  ")
    print(" | |    | |   |  |   | |    | ||  ____  ||  ______|   /  /   |  "
          "|\   /|  ||  |         |_  \  ")
    print(" | |    | |   |  |   | |    | || |    | || |______   /  /    |  "
          "| \_/ |  ||  |           \  \ ")
    print(" | \____/ |   |  |   | \____/ || |____| ||        | /  /____ |  "
          "|     |  ||  |      /\____)  )")
    print("  \______/    [__]    \______/ [________]|________||________||__"
          "|     |__||__|      \_______/ ")
    print("----------------------------------------------------------------"
          "------------------------------ \n \n")


"""Executes "clear" on terminal, removing all text and flushing the buffer."""

def clear():
    os.system("clear")


"""Confirms if the local info file is present in the curent working directory.
Returns "True" if it is. Otherwise, returns "False".
"""

def check_local_inf():
    if os.path.isfile("local_inf"):
        print("Local_inf data found! \n")
        return True
    print("Local_inf data not found. Resuming... \nl")
    return False


"""Opens file containing readable local info and returns a list containing: 
Dropbox API key, Dropbox destination path,and local destination path.
"""

def retrieve_local_inf():
    with open("local_inf", 'r') as file:
        contents = file.read()
        information = contents.splitlines()
    return information


"""Checks all outdated python modules needed for the running of this program 
and updates the modules if they are outdated.
Returns a string containing the names of all the programs that were updated.
"""

def update_packages(update_check):
    if update_check.lower() in ('y', "yes"):
        print("----------------------------------------------------------"
              "------------------------------------")
        print('Checking for Module Updates...')
        print("----------------------------------------------------------"
              "------------------------------------ \n")
        updated_programs = ''
        update_log = sp.Popen(["pip list --outdated"],
                              shell=True,
                              stdout=sp.PIPE)
        output = update_log.communicate()[0]
        in_vir_env = False
        confirm = ('y', "yes")
        deny = ('n', "no")
        # Checks if python is currently being run on a virtual environment
        if (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
            in_vir_env = True
        # Module named "youtube_dl" but update_log names the module "youtube-dl"
        if b"youtube-dl" in output:
            if in_vir_env:
                while True:
                    youtube_ans = input(
                        "youtube_dl is outdated and updating it "
                        "is necessary to run. Would you like to "
                        "update the module on your virtual "
                        "environment?: \n"
                        "(reply with 'y' to update and 'n' to "
                        "quit) \n")
                    youtube_ans = youtube_ans.lower()
                    if youtube_ans in confirm:
                        os.system("pip install --upgrade youtube_dl")
                        updated_programs += "youtube-dl"
                        break
                    elif youtube_ans in deny:
                        sys.exit()
                    else:
                        print("Invalid answer. Please try again.")
            # (Non-virtual environment case) Might need password if not admin
            else:
                while True:
                    youtube_ans = input(
                        "youtube_dl is outdated and updating it "
                        "is necessary to run. Would you like to "
                        "update the module?: \n"
                        " (Note: Admin access is required! If "
                        "prompted, you may need your computer's "
                        "user password. \n"
                        "reply with 'y' to update and 'n' to "
                        "quit) \n")
                    if youtube_ans in confirm:
                        os.system("sudo -H pip install --upgrade youtube_dl")
                        updated_programs += "youtube-dl"
                        break
                    elif youtube_ans in deny:
                        sys.exit()
                    else:
                        print("Invalid answer. Please try again.")
        if b"dropbox" in output:
            while True:
                dropbox_ans = input(
                    "The dropbox module is outdated. Would you "
                    "like to update the module?: \n"
                    "(reply with 'y' to update or 'n' to skip) \n")
                dropbox_ans = dropbox_ans.lower()
                if dropbox_ans in confirm:
                    os.system("pip install --upgrade dropbox")
                    updated_programs += " dropbox"
                    break
                elif dropbox_ans in deny:
                    break
                else:
                    print("Invalid answer. Please try again.")
        # Note: Don't update eyed3, doesn't function as intended after ver. 0.8.10
        print("\n----------------------------------------------------"
              "------------------------------------------")
        print("The following modules have been updated: " + updated_programs +
              "\nResuming...")
        print("------------------------------------------------------"
              "---------------------------------------- \n")
        return True
    # Continue the program without updating
    elif update_check.lower() in ('n', "no"):
        print("----------------------------------------------------------"
              "------------------------------------")
        print('Resuming...')
        print("----------------------------------------------------------"
              "------------------------------------ \n")
        return True
    else:
        clear()
        print("No option was provided. \n")
        return False


"""Accepts a string containing a single block of text of Youtube URL's and 
returns a separated list of them into elements.
"""

def url_to_list(link_string: str):
    # If there are any spaces, eliminate them all
    escaped_string = (link_string.replace('\r',
                                          '\\r').replace('\n', '\\n').replace(
                                              '\t', '\\t'))
    list_string = ' '.join(escaped_string.split())
    print('\n list_string: ' + list_string)
    url_search = re.findall((r"(https?://)?(www\.)?"
                             "(youtube|youtu|youtube-nocookie)(.)(com|be)(/)"
                             "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"),
                            list_string)
    links = []
    for item in url_search:
        links.append(''.join(item))
    return links


"""Retrieves Youtube video's filename from a url and a youtube_dl instance."""

def get_filename(url: str, ydl: Type[youtube_dl.YoutubeDL]):
    info_dict = ydl.extract_info(url, download=False)
    # Retrieves the name of the file as opposed to the title of the video.
    # OS issues if title is taken instead.
    filename = ydl.prepare_filename(info_dict)
    # Removes the entire path and leaves just the filname
    separate_path = os.path.basename(filename)
    print(separate_path)
    # Removes the file extension from the filename
    final_name = os.path.splitext(separate_path)[0]
    print(final_name)
    return final_name


"""Outputs the Youtube Video title and index placement 
amongst the current batch of videos through the Terminal window.
"""

def display_title(video_name: str, index: int, video_total: int):
    print("------------------------------------------------------------------"
          "---------------------------- \n")
    print(
        "Downloading Youtube videos " + str(index + 1) + " out of " +
        str(video_total) + "\n", "(Title: " + video_name + ") \n")
    print("------------------------------------------------------------------"
          "---------------------------- \n")
    return None


"""Given a string representing a Youtube video title, 
returns the same string but with problematic characters removed.
"""

def replace_characters(char_check: str):
    if '&#39;' in char_check:
        # Apostrophe in decimal
        char_check = char_check.replace("&#39;", "'")
    if '&amp;' in char_check:
        # Ampersand in decimal
        char_check = char_check.replace("&amp;", '&')
    if '&quot;' in char_check:
        # Quote in decimal
        char_check = char_check.replace("&quot;", '"')
    if '/' in char_check:
        char_check = char_check.replace('/', '_')
    return char_check


"""Primary conversion method.
Passes a Youtube URL into youtube_dl and 
exports the video file to the out_directory location.
Returns the filename of the recently created mp3 along with a boolean 
determining whether a file with the same name already existed. 
If error is found, return False with the boolean described above instead.  
"""

# Might have issues based on out_directory
def url_to_video(url: str, out_directory: str, video_count: int):
    # Variable checking if music file already exists in the directory
    duplicate_exists = False
    ydl_opts = {
        'format':
        'bestaudio/best',
        'outtmpl':
        os.path.join(out_directory, '%(title)s.%(ext)s'),
        #'rejecttitle': 'True',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractaudio':
        'True',
        'audioformat':
        'mp3',
        'nooverwrites':
        'True',
        'noplaylist':
        'True',
        'nocheckercertificate':
        'True'
    }
    # Use 'quiet' in ydl_opts to not print messages to stdout
    # 'quiet': True
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            orig_title = get_filename(url[1], ydl)
    except gaierror as e:
        clear()
        raise Exception("The following connection error has been spotted. \n" +
                        str(e) + "\n Please establish an internet "
                        "connection first. \nExiting...") from None
    if orig_title == None:
        print("----------------------------------------------------------"
              "------------------------------------ \n")
        print("No title was found for the given URL: \n " + url[1] + "\n",
              "Resuming... \n")
        print("----------------------------------------------------------"
              "------------------------------------ \n")
        return False, duplicate_exists
    else:
        rmv_char = replace_characters(orig_title)
        artist_check = artist_from_title(rmv_char)
        display_title(artist_check[0], url[0], video_count)
        # For modules that require extensions like os, eye3d and Dropbox
        new_mp3_name = artist_check[0] + '.mp3'
        new_mp3_path = os.path.join(out_directory, new_mp3_name)
        print('new_mp3_path: ' + new_mp3_path)
        duplicate_exists = verify_file_or_dir(new_mp3_path, 'file')
        print(duplicate_exists)
        if duplicate_exists:
            # Duplicate file found with the same title,
            # don't replace by downloading a new one!
            print("duplicate_exists!")
            return new_mp3_name, duplicate_exists
        else:
            extension_rem = new_mp3_name[:-3]
            ydl_opts['outtmpl'] = os.path.join(out_directory,
                                               extension_rem + '%(ext)s')
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url[1]])
            # Handles any URL's that aren't from Youtube
            except youtube_dl.utils.DownloadError:
                clear()
                print(
                    "DownloadError: Video cannot be accessed. Please check"
                    "the URL's, internet connection, or presence of ffmpeg on device."
                )
                return False, duplicate_exists
            except youtube_dl.utils.UnavailableVideoError:
                clear()
                print("UnavailableVideoError: Video is currently unavailable")
                return False, duplicate_exists
            except AttributeError:
                clear()
                print(" The Youtube URL's provided were invalid.")
                return False, duplicate_exists
            # Update song metadata if artist_from_title
            # returns a tuple of the new song title and artist name
            if artist_check[1] != None:
                set_artist(new_mp3_path, artist_check[1])
            return new_mp3_name, duplicate_exists


"""Extracts the artist information from a given title and 
returns both the new song title and artist name.
If no artist is found, returns a tuple of original input song name and None.
"""

def artist_from_title(song: str):
    hyphen_check = song.rfind("-")
    if hyphen_check:
        new_title = song[song.rfind("-") + 1:]
        valid_title = re.search('[a-zA-Z]',
                                new_title)  # if nothing in hyphen's right
        if valid_title == None:
            return song, None
        new_title = ' '.join(new_title.split())
        no_hyphens = song.replace("-", " ")
        artist_extract = no_hyphens[:hyphen_check]
        return new_title, artist_extract
    else:
        return song, None


"""Takes the artist's name extracted from the title 
and places it in the mp3 file's 'artist' meta data instead.
"""

def set_artist(song_path: str, artist_name: str):
    print("song_path: " + song_path)
    audio_file = eyed3.load(song_path)
    audio_file.tag.artist = artist_name
    audio_file.tag.save()
    return None


"""Deletes all video, video segment, or music files inside a dictionary
found within the current working directory.
"""

def delete_items(list: list):
    # Iteration over the key strings of the video dictionary
    for file in list:
        try:
            os.remove(file)
        # Either the music file no longer exists
        # or already deleted (in the case of duplicate URL's)
        except FileNotFoundError:
            pass
    return None


"""Given a path and a string representing that the input is a directory, 
return True if the give directory exist and False otherwise.
Given a path and a string representing that the input is a filename,
return True if the file exists and False otherwise.
"""

def verify_file_or_dir(path: str, destination: str):
    if destination == 'dir':
        if os.path.isdir(path):
            return True
        else:
            clear()
            print("Invalid path, please provide a valid path.")
            return False
    if destination == 'file':
        if os.path.isfile(path):
            return True
        else:
            clear()
            return False


"""Main operator function that takes a list of Youtube URL's + a directory 
and downloads/converts the URL's to mp3 files into the directory.
"""

def create_mp3(link_list: list, dir: str):
    # Saves the current working directory
    saved_CWD = os.getcwd()
    if dir != saved_CWD:
        # Changes the main directory to another location
        os.chdir(dir)
    # The 0th item in the dict is updated
    # if any of the files in link_list have a front slash in the file name
    music_list = []
    delete_exemption = []
    for url in enumerate(link_list):
        extract_check = url_to_video(url, dir, len(link_list))
        if extract_check[0]:
            # Adds the current mp3 filename to a list
            # that will prevent the file from being deleted in case of error
            if extract_check[1]:
                delete_exemption.append(extract_check[0])
                print("delete_exemption: " + str(delete_exemption))
            music_list.append(extract_check[0])
        elif not extract_check[0]:
            current_directory_state = os.listdir(dir)
            to_delete = []
            for file in current_directory_state:
                # Checks if the file being observed
                # has the same name as the video title.
                # (Perhaps a better way to do this?)
                if file in music_list:
                    if file not in delete_exemption:
                        to_delete.append(file)
            delete_items(to_delete)
            return
    # Reverts the main directory back
    os.chdir(saved_CWD)
    print('Music list: ' + str(music_list))
    return music_list

def authenticate_gdrive(scopes):
    creds = None
    # token.pickle stores the user's access and refresh tokens, and is created 
    # automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if not os.path.exists("credentials.json"):
            return """'credential.json' file is not detected in working directory. \nRelocate the file to the UTube2MP3 project folder or follow the steps \nin the link below to allow API access to your Google Drive. \n(up to 'Configure the Sample' section, where instead you can rerun this program: \nhttps://developers.google.com/drive/api/quickstart/python"""
        if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service, need cache_discovery and static_discovery
    try:
        #return build('drive', 'v3', credentials=creds)
        return build('drive', 'v3', credentials=creds, cache_discovery=False, static_discovery=False)
    except UnknownApiNameOrVersion: 
        return "Error encountered with creating the API service, check the service name and version."

def upload_to_gdrive(gdrive_service, mp3_list, dest_folder_id):
    for filename in mp3_list:
        # first, define file metadata, such as the name and the parent folder ID
        file_metadata = {
            "name": filename,
            "parents": [dest_folder_id]
        }
        media = MediaFileUpload(filename, resumable=True)  
        # upload
        file = gdrive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print("FILE UPLOADED, filename:", filename)

def main():
    # terminal is wide enough to print ASCII art
    if os.get_terminal_size()[0] >= 94:
        print_ASCII()
    # print program name using ANSI text colors
    else:
        print("\033[1;32m UTube2MP3 \033[39m \n")
    
    # Which aspect of API is being accessed, if modifying, delete token.pickle
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    modules_updated = False
    dest_folder_id = ""
    mp3_to_drive = False
    resume = True
    created_mp3 = False
    conversion_ready = False
    local_data_exists = check_local_inf()
    if local_data_exists:
        dest_folder_id, local_destination = retrieve_local_inf()

    #DON'T FORGET TO TEST THE TOKEN.PICKLE AND MISSING CREDENTIALS TOWARDS THE END OF ALL THE RE-INTEGRATION
    #Loop for user input on whether modules should be updated or not
    while not modules_updated:
        update_check = input("Would you like to check for module updates? \n"
                             "(reply with 'y' to check or 'n' to continue) \n")
        modules_updated = update_packages(update_check)
    # Conversion process restarts if user wishes to resume converting
    while resume:
        # Dropbox or Local Directory input loop
        while not conversion_ready:
            local_or_drive = input("Would you like to save the files to "
                                    "Google Drive or to a local directory?: \n"
                                    "(reply with 'g' for Google Drive and 'l' for"
                                    " local directory) \n").lower()
            if local_or_drive.lower() in ('g', "google", "drive", "google drive", "gdrive"):
                mp3_to_drive = True 
                # Used for create_mp3 method
                directory = os.getcwd()
                if local_data_exists:
                    # Call the Drive v3 API
                    service = authenticate_gdrive(SCOPES)
                    conversion_ready = True
                else:
                    service = ""
                    # leave loop when service returns a googleapiclient.discovery.Resource object
                    # This will happen when the token.pickle file is produced
                    while type(service) == str:
                        service = authenticate_gdrive(SCOPES)
                    # Dropbox directory input loop
                    while not dest_folder_id:
                        dest_folder_id = input(
                            "\n \nPlease provide the folder id of the "
                            "Google Drive directory where the "
                            ".mp3 files will be placed in: "
                            "\n"
                            "(Note: the id is the series of numbers and letters \n"
                            "found in the URL of your folder's web page, below is an example): \n"
                         "https://drive.google.com/drive/folders/\033[1;32mXXxx1234567890xxXX\033[39m \n"
                            "The id must be valid and precise. Otherwise, "
                            "the program will raise an error\n")
                    conversion_ready = True
            elif local_or_drive.lower() in ('l', "local", "localdirectory",
                                             "local directory"):
                if not local_data_exists:
                    while not is_valid_directory:
                        directory = input(
                            "\n \nPlease paste the path that you "
                            "would like your music to be downloaded"
                            " to: \n")
                        if directory:
                            is_valid_directory = verify_file_or_dir(
                                directory, 'dir')
                        else:
                            clear()
                            print("No path was provided.")
                    conversion_ready = True
                else:
                    conversion_ready = True
            else:
                clear()
                print("Invalid Input. Please try again. \n")
        # Youtube URL to mp3 input loop
        while not created_mp3:
            unconv_songs = input("\n \nPlease paste the URL's of the music "
                                 "that is to be converted: \n")
            # Empty string was provided
            if not unconv_songs:
                clear()
                print("No URL's were provided.")
            else:
                # Executes the conversion process.
                # Returns a dictionary with the music that was converted.
                url_list = url_to_list(unconv_songs)
                mp3_list = create_mp3(url_list, directory)
                # mp3Dict came back with no errors.
                # Transfer to Google Drive or go back to Youtube URL input loop
                if mp3_list:
                    created_mp3 = True
        if mp3_to_drive:
            print("----------------------------------------------------------"
                  "------------------------------------")
            print('Now Transfering files to Google Drive...')
            print("----------------------------------------------------------"
                  "------------------------------------ \n")
            upload_to_gdrive(service, mp3_list, dest_folder_id)
            print("----------------------------------------------------------"
                  "------------------------------------")
            print('Now Deleting mp3 Files Locally...')
            print("----------------------------------------------------------"
                  "------------------------------------ \n")
            delete_items(mp3_list)
        print("--------------------------------------------------------------"
              "--------------------------------")
        print('Finished!')
        print("--------------------------------------------------------------"
              "-------------------------------- \n")

        # Continue mp3 Creation input Loop
        while True:
            resume_response = input("Would you like to resume converting "
                                    "Youtube Videos?: \n"
                                    "(reply with 'y' to continue and 'n' to "
                                    "quit)\n")
            resume_response = resume_response.lower()
            if resume_response.lower() in ('y', "yes"):
                mp3_to_drive = False
                created_mp3 = False
                conversion_ready = False
                break
            elif resume_response.lower() in ('n', "no"):
                resume = False
                break
            else:
                clear()
                print("No option was provided.")

main()
