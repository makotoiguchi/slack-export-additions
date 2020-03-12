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

# Process JSON message files from export_folder
def adjust_json_msg_files(input_folder, newurl, newurl_tmb):
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
            for i, line in enumerate(fileinput.input(json_file, inplace=True)):
                # Match download link
                line, modified = parse_and_replace(line, re_link_files, newurl)
                if (not modified):
                    line, modified = parse_and_replace(line, re_link_files2, newurl)
                
                    if (not modified):
                        # Match Thumbnail link
                        line, _ = parse_and_replace(line, re_link_thumb, newurl_tmb)
                
                print(line, end='')


# Parse and replace JSON file in place
def parse_and_replace(line, pattern, newurl):   
    matched = pattern.match(line)
    modified = False
    if (matched != None):
        # parse link
        url = matched.group(1)
        folder = matched.group(2)
        filename = matched.group(3)
        
        # replace links
        new_file_location = newurl + "/" + folder + "/" + filename
        line = line.replace(url, new_file_location)
        modified = True
    # return modified / unmodified line
    return line, modified


# MAIN
if (__name__ == "__main__"):
    # Args
    parser = argparse.ArgumentParser(description="Adjust JSON files with the local links")
    parser.add_argument('--input', required=True, help="Export folder created by slack-export")
    parser.add_argument('--newurl', required=True, help="server URL")
    args = parser.parse_args()
    
    # clear trailing "/"
    newurl = args.newurl
    while (newurl.endswith("/")):
        newurl = newurl[:-1]

    newurl_tmb = newurl + "/tmb"

    adjust_json_msg_files(args.input, newurl, newurl_tmb)
    