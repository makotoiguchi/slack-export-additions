#!/usr/bin/env python3
#
#    input: files exported by: https://github.com/zach-snell/slack-export/
#    reference: https://github.com/auino/slack-downloader/blob/master/slack-downloader.py
#
import argparse
import os
import json
import re
import fileinput
import requests
#

# create subfolder
def create_subfolder(folder, subfolder_name):
    subfolder = os.path.join(folder, subfolder_name)
    print("Creating subfolder", subfolder)
    try:
        os.stat(subfolder)
    except:
        os.mkdir(subfolder)
    return subfolder 

# Process JSON message files from export_folder
def process_json_msg_files(input_folder, output_folder, output_tmb_folder, token):
    print("Processing:", input_folder)

    # patterns to search
    re_link_files = re.compile("                \"url[a-z_0-9]+\": \"(https?://files.slack.com/files-pri/([^/]+)/download/([^\"]+))\"")
    re_link_files2 = re.compile("                \"url[a-z_0-9]+\": \"(https?://files.slack.com/files-pri/([^/]+)/([^\"]+))\"")
    re_link_thumb = re.compile("                \"thumb[a-z_0-9]+\": \"(https?://files.slack.com/files-tmb/([^/]+)/([^\"]+))\"")

    # scan on slack-export folder for subfolders (channels, groups, DMs)
    print("Inspecting subfolders")
    subfolders = [ f.path for f in os.scandir(input_folder) if f.is_dir() ]

    for group_folder in subfolders:
        # only process json files = messages files
        print("-- Processing:", group_folder)
        json_files = [ os.path.join(group_folder, f.name) for f in os.scandir(group_folder) if (f.is_file() and f.name.endswith(".json")) ]
        for json_file in json_files:
            print("-- -- JSON:", json_file)
            for i, line in enumerate(fileinput.input(json_file)):
                # Match download link
                if (parse_and_download(line, re_link_files, output_folder, token)):
                    continue
                if (parse_and_download(line, re_link_files2, output_folder, token)):
                    continue
                
                # Match Thumbnail link
                parse_and_download(line, re_link_thumb, output_tmb_folder, token)


# Parse and trigger download
def parse_and_download(line, pattern, dest_folder, token):
    matched = pattern.match(line)
    if (matched != None):
        # parse link
        url = matched.group(1)
        folder = matched.group(2)
        filename = matched.group(3)
        
        # prepare download file
        download_folder = create_subfolder(dest_folder, folder)
        local_filename = os.path.join(download_folder, filename)
        print(line)
        if (download_slack_file(url, local_filename, token)):
            print("Saved!")
            return True
        else:
            print("Failed.")
    return False

# Download Slack file. Token needed
def download_slack_file(url, local_filename, token):
    try:
        print("Saving to", local_filename, "...", end="")
        headers = {'Authorization': 'Bearer '+token}
        r = requests.get(url, headers=headers)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
    except: 
        return False
    return True


# MAIN
if (__name__ == "__main__"):
    # Args
    parser = argparse.ArgumentParser(description="Download Slack files and adjust JSON files")
    parser.add_argument('--input', required=True, help="Export folder created by slack-export")
    parser.add_argument('--token', required=True, help="Slack API token")
    args = parser.parse_args()
    
    # create destination folder
    files_folder = create_subfolder(args.input, "files")
    files_tmb_folder = create_subfolder(files_folder, "tmb")
    
    process_json_msg_files(args.input, files_folder, files_tmb_folder, args.token)
    