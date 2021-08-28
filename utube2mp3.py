"""Created by Andrew Yeon on July 17, 2018."""

import os
import sys
import re
import subprocess as sp
from collections import OrderedDict
from socket import gaierror
from typing import Type

from requests.exceptions import ConnectionError
import stone


current_error_mess = ''
try:
    current_error_mess = '(pip install youtube_dl)'
    import youtube_dl
    current_error_mess = '(pip install dropbox)'
    import dropbox
    current_error_mess = ("('pip install eyed3==0.8.10' and then 'pip"
                          "install python-magic-bin==0.4.14')"
                          )
    import eyed3
except ImportError:
    raise Exception("Please install the following python package before", 
                    "proceeding, otherwise the program will not function",
                    "properly: "
                    + current_error_mess + "\n"
                    ) from None


def print_ASCII():
    print("----------------------------------------------------------------"
          "------------------------------"
          )
    print("  _      _  ________  _      _  ________  ________   ______   __"
          "       __  _______   ________ "
          )   
    print(" | |    | ||__    __|| |    | ||   __   ||        | /  _   \ |  "
          "\     /  ||  ____ \ |_____   |"
          )
    print(" | |    | |   |  |   | |    | || |____|_||  ______||__/ /  | |  "
          " \   /   || |____| |     /  / "
          )
    print(" | |    | |   |  |   | |    | ||      <_ | |______     /  /  |  "
          "  \_/    ||   ____/     /  /  "
          )
    print(" | |    | |   |  |   | |    | ||  ____  ||  ______|   /  /   |  "
          "|\   /|  ||  |         |_  \  "
          )
    print(" | |    | |   |  |   | |    | || |    | || |______   /  /    |  "
          "| \_/ |  ||  |           \  \ "
          )
    print(" | \____/ |   |  |   | \____/ || |____| ||        | /  /____ |  "
          "|     |  ||  |      /\____)  )"
          )
    print("  \______/    [__]    \______/ [________]|________||________||__"
          "|     |__||__|      \_______/ "
          )
    print("----------------------------------------------------------------"
          "------------------------------ \n \n"
          )
    return None

"""Executes "clear" on terminal, removing all text and flushing the buffer."""
def clear():
    os.system("clear")
    return None

"""
Opens file containing readable local info and returns a list containing: 
Dropbox API key, Dropbox destination path,and local destination path.
""" 
def retrieve_local_inf():
    if os.path.isfile("local_inf"):
        with open("local_inf", 'r') as file:
            contents = file.read()
            information = contents.splitlines()
        print("Local_inf data found! \n")
        return information
    else:
        print("Local_inf data not found. Resuming... \nl")
        return False
 

"""
Checks all outdated python modules needed for the running of this program 
and updates the modules if they are outdated.
Returns a string containing the names of all the programs that were updated.
"""  
def update_packages():
    updated_programs = ''
    update_log = sp.Popen(["pip list --outdated"],
                          shell = True, 
                          stdout = sp.PIPE
                          )
    output = update_log.communicate()[0]
    in_vir_env = False
    confirm = ('y', "yes")
    deny = ('n', "no")
    # Checks if python is currently being run on a virtual environment
    if (hasattr(sys, 'real_prefix')
            or (hasattr(sys, 'base_prefix') 
                    and sys.base_prefix != sys.prefix)):
        in_vir_env = True
    # Module named "youtube_dl" but update_log names the module "youtube-dl"
    if b"youtube-dl" in output:
        if in_vir_env:
            while True:
                youtube_ans = input("youtube_dl is outdated and updating it "
                                    "is necessary to run. Would you like to "
                                    "update the module on your virtual "
                                    "environment?: \n" 
                                    "(reply with 'y' to update and 'n' to "
                                    "quit) \n"
                                    )
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
                youtube_ans = input("youtube_dl is outdated and updating it "
                                    "is necessary to run. Would you like to "
                                    "update the module?: \n" 
                                    " (Note: Admin access is required! If "
                                    "prompted, you may need your computer's "
                                    "user password. \n" 
                                    "reply with 'y' to update and 'n' to "
                                    "quit) \n"
                                    )
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
            dropbox_ans = input("The dropbox module is outdated. Would you "
                                "like to update the module?: \n" 
                                "(reply with 'y' to update or 'n' to skip) \n"
                                )
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
    return updated_programs


"""
Takes a token and some local resource file and 
returns an authenticated, logged-in Dropbox Access Account if found.
"""
def create_dropbox_request(token: str, local_inf: list):
    if token:
        dbx = dropbox.Dropbox(token)
        try:
            dbx.check_user()
            return dbx
        except dropbox.exceptions.AuthError:
            clear()
            print('Invalid access token was provided.')
            return False
    else:
        if local_inf:
            dbx = dropbox.Dropbox(local_inf[0])
            return dbx
        else:
            clear()
            print("No access token was provided. Please provide an access "
                  "token to continue."
                  )
            return False


"""
Takes a Dropbox account, a file path, and some local resource file and 
returns the filepath of a valid path.
of a DB account or False if no such filepath was found for the account.
"""
def check_dropbox_path(db: Type[dropbox.Dropbox],path: str,local_inf: list):
    if path:
        try:
            db.files_alpha_get_metadata(path)
            return path
        # Dropbox SDK currently has a dependancy issue for invalid paths.
        # Use validation straight from stone module.
        except stone.backends.python_rsrc.stone_validators.ValidationError:
            clear()
            print("Invalid Dropbox path was provided. Please provide an "
                  "existing Dropbox directory to continue."
                  )
            return False
    else:
        if local_inf:
            return local_inf[1]
        else:
            clear()
            print("No path was provided. Please provide a proper Dropbox path"
                  "to continue."
                  )
            return False


"""
Accepts a string containing a single block of text of Youtube URL's and 
returns a separated list of them into elements.
"""
def url_to_list(link_string: str):
    # If there are any spaces, eliminate them all
    escaped_string = (link_string.replace('\r','\\r')
                      .replace('\n','\\n')
                      .replace('\t','\\t')
                      )
    list_string = ' '.join(escaped_string.split())
    print('\n list_string: ' + list_string)
    url_search = re.findall((r"(https?://)?(www\.)?"
                             "(youtube|youtu|youtube-nocookie)(.)(com|be)(/)"
                             "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
                             )
                             , list_string
                             )
    links = []
    for item in url_search:
        links.append(''.join(item))
    return links
    


"""Retrieves Youtube video's filename from a url and a youtube_dl instance."""
def get_filename(url: str, ydl: Type[youtube_dl.YoutubeDL]):
    info_dict = ydl.extract_info(url, download = False)
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


"""
Outputs the Youtube Video title and index placement 
amongst the current batch of videos through the Terminal window.
"""
def display_title (video_name: str, index: int, video_total: int):
    print("------------------------------------------------------------------"
          "---------------------------- \n"
          )
    print("Downloading Youtube videos " + str(index + 1) + " out of " + 
          str(video_total) + "\n",  
          "(Title: " + video_name + ") \n")
    print("------------------------------------------------------------------"
          "---------------------------- \n")
    return None

"""
Given a string representing a Youtube video title, 
returns the same string but with problematic characters removed.
"""
def replace_characters(char_check: str):
    if '&#39;' in char_check:
        # Apostrophe in decimal
        char_check = char_check.replace("&#39;","'") 
    if '&amp;' in char_check:
        # Ampersand in decimal
        char_check = char_check.replace("&amp;",'&')
    if '&quot;' in char_check:
        # Quote in decimal
        char_check = char_check.replace("&quot;",'"')
    if '/' in char_check:
        char_check = char_check.replace('/','_')
    return char_check


"""    
Primary conversion method.
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
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_directory, '%(title)s.%(ext)s'), 
        'rejecttitle': 'True', 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
        'extractaudio': 'True',
        'audioformat': 'mp3',
        'nooverwrites': 'True',
        'noplaylist': 'True'
        }
    # Use 'quiet' in ydl_opts to not print messages to stdout
    # 'quiet': True 
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            orig_title = get_filename(url[1], ydl)
    except gaierror as e:
        clear()
        raise Exception("The following connection error has been spotted. \n"
                    + str(e) + "\n Please establish an internet "
                    "connection first. \nExiting..."
                    ) from None 
    if orig_title == None:
        print("----------------------------------------------------------"
            "------------------------------------ \n"
            )
        print("No title was found for the given URL: \n " + url[1] + "\n",
            "Resuming... \n"
            )
        print("----------------------------------------------------------"
            "------------------------------------ \n"
            )
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
                print("DownloadError: Video cannot be accessed. Please check"
                    " the URL's or your internet connection and try again."
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
    


"""
Extracts the artist information from a given title and 
returns both the new song title and artist name.
If no artist is found, returns a tuple of original input song name and None.
"""    
def artist_from_title(song: str):
    hyphen_check = song.rfind("-")
    if hyphen_check:
        new_title = song[song.rfind("-") + 1:]
        new_title = ' '.join(new_title.split())
        no_hyphens = song.replace("-"," ")
        artist_extract = no_hyphens[:hyphen_check]
        return new_title, artist_extract
    else:
        return song, None


"""
Takes the artist's name extracted from the title 
and places it in the mp3 file's 'artist' meta data instead.
"""
def set_artist(song_path: str,artist_name: str):
    audio_file = eyed3.load(song_path)
    audio_file.tag.artist = artist_name
    audio_file.tag.save()
    return None


"""
Deletes all video, video segment, or music files inside a dictionary
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


"""
Given a path and a string representing that the input is a directory, 
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


"""
Main operator function that takes a list of Youtube URL's + a directory 
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
        extract_check = url_to_video(url, 
                                     dir, 
                                     len(link_list)
                                     )
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


"""
Takes a Dropbox Object + list of mp3 filenames + remote directory string name
and uploads the music files to the given remote directory.
"""
def upload_to_dropbox(dbx_account: Type[dropbox.Dropbox], 
                      mp3_files: list, 
                      remoteDir: str):
    for music in mp3_files:
        # The last 4 indices that contain the ".mp3" file extension
        # will be removed for print presentation
        print("Uploading MP3: " + music[:-4])
        with open(music, 'rb') as music_file:
            try:
                dbx_account.files_upload(music_file.read(), 
                                         remoteDir + "/" +  music
                                         )
            except ConnectionError as e:
                # Delete every single mp3 because connection error 
                # instantly ends the program. (Change if timer is made!)
                delete_items(mp3_files)
                clear()
                raise Exception("The following connection error has been "
                                "spotted: \n \n" + str(e) + "\n \n Please "
                                "establish an internet connection first. "
                                "\nExiting..."
                                ) from None  
    return None


def main():
    print_ASCII()
    
    modules_updated = False
    mp3_to_dropbox = False
    resume = True
    created_mp3 = False
    conversion_ready = False
    local_inf = retrieve_local_inf()
    
    #Loop for user input on whether modules should be updated or not
    while not modules_updated: 
        update_check = input("Would you like to check for module updates? \n"
                             "(reply with 'y' to check or 'n' to continue) \n"
                             )
        if update_check in ('y', "yes"):
            print("----------------------------------------------------------"
                  "------------------------------------"
                  )
            print('Checking for Module Updates...')
            print("----------------------------------------------------------"
                  "------------------------------------ \n"
                  )
            
            updated = update_packages()
            if updated:
                print("\n----------------------------------------------------"
                      "------------------------------------------"
                      )
                print("The following modules have been updated: " + updated + 
                      "\nResuming..."
                      )
                print("------------------------------------------------------"
                      "---------------------------------------- \n"
                      )
                modules_updated = True
            else:
                print("------------------------------------------------------"
                      "----------------------------------------"
                      )
                print('All modules have been accounted for! \nResuming...')
                print("------------------------------------------------------"
                      "---------------------------------------- \n"
                      )
                modules_updated = True
        elif update_check in ('n', "no"):
            print("----------------------------------------------------------"
                  "------------------------------------"
                  )
            print('Resuming...')
            print("----------------------------------------------------------"
                  "------------------------------------ \n"
                  )
            modules_updated = True
        else:
            clear()
            print("No option was provided. \n")       
    # Conversion process restarts if user wishes to resume converting
    while resume:
        # Dropbox or Local Directory input loop
        while not conversion_ready:
            comp_or_dropbox = input ("Would you like to save the files to "
                                     "Dropbox or to a local directory?: \n" 
                                     "(reply with 'd' for Dropbox and 'l' for"
                                     " local directory) \n"
                                     ).lower()
            if comp_or_dropbox in ('d', 
                                   "dropbox", 
                                   "drop"):
                mp3_to_dropbox = True
                retype_token = True
                valid_dropbox_directory = False
                dbx = False
                # Used for create_mp3 method
                directory = os.getcwd()
                # Main Dropbox Path Loop
                # Returns here if access token is invalid
                while retype_token:
                    # Dropbox API access token input loop
                    while dbx is False:
                        access_token = input("\n \nPlease provide the Dropbox"
                                             " API access token: \n"
                                             "(Note: the token must be "
                                            "accurate or the files can't "
                                            "access your Dropbox account) \n"
                                            )
                        # If the access token was invalid, 
                        # continue Dropbox API access token input loop.
                        dbx = create_dropbox_request(access_token,local_inf)
                    # Dropbox directory input loop
                    while not valid_dropbox_directory:
                        dbx_directory = input("\n \nPlease provide the "
                                              "Dropbox directory where the "
                                              ".mp3 files will be placed in: "
                                              "\n"
                                              "(Note: The directory must be "
                                              "valid and precise. Otherwise, "
                                              "the program may not finish)\n"
                                              )
                        path_exists = check_dropbox_path(dbx,
                                                         dbx_directory,
                                                         local_inf
                                                         )
                        # Validation Error: The Dropbox path was invalid. 
                        # Returns to beginning of Dropbox directory input loop.
                        if not path_exists:
                            pass
                        # The Dropbox directory was able to retrieve metadata
                        else:
                            retype_token = False
                            valid_dropbox_directory = True   
                conversion_ready = True 
            elif comp_or_dropbox in ('l', 
                                     "local", 
                                     "localdirectory", 
                                     "local directory"):
                while True:
                    directory = input("\n \nPlease paste the path that you "
                                      "would like your music to be downloaded"
                                      " to: \n"
                                      )
                    if directory:
                        is_valid = verify_file_or_dir(directory, 'dir')
                        if is_valid:
                            break
                    else:
                        if local_inf:
                            directory = local_inf[2]
                            break
                        else:
                            clear()
                            print("No path was provided.") 
                conversion_ready = True
            else:
                clear()
                print("Invalid Input. Please try again. \n")
        # Youtube URL to mp3 input loop
        while not created_mp3:
            unconv_songs = input("\n \nPlease paste the URL's of the music "
                                 "that is to be converted: \n"
                                 )
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
                # Transfer to Dropbox or go back to Youtube URL input loop
                if mp3_list:
                    created_mp3 = True
        if mp3_to_dropbox:
            print("----------------------------------------------------------"
                 "------------------------------------"
                 )
            print('Now Transfering files to Dropbox...')
            print("----------------------------------------------------------"
                  "------------------------------------ \n"
                  )
            if not dbx_directory:
                # If input for Dropbox directory is an empty string 
                # and local_inf exists, 
                # then set local_inf path as default Dropbox path 
                dbx_directory = path_exists
            upload_to_dropbox(dbx, 
                              mp3_list, 
                              dbx_directory
                              )
            print("----------------------------------------------------------"
                  "------------------------------------"
                  )
            print('Now Deleting mp3 Files Locally...')
            print("----------------------------------------------------------"
                  "------------------------------------ \n"
                  )    
            delete_items(mp3_list)
        print("--------------------------------------------------------------"
              "--------------------------------"
              )
        print('Finished!')
        print("--------------------------------------------------------------"
              "-------------------------------- \n"
              )

        # Continue mp3 Creation input Loop
        while True:
            resume_response = input("Would you like to resume converting "
                                    "Youtube Videos?: \n"
                                    "(reply with 'y' to continue and 'n' to "
                                    "quit)\n"
                                    )
            resume_response = resume_response.lower()
            if resume_response in ('y', "yes"):
                mp3_to_dropbox = False
                created_mp3 = False
                conversion_ready = False
                break
            elif resume_response in ('n', "no"):
                resume = False
                break
            else:
                clear()
                print("No option was provided.")


main()