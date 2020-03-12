#!/usr/bin/env python3
#
#    input: files exported by: https://github.com/zach-snell/slack-export/
#
import argparse
import os
import json
import re
import fileinput
#

# Load user info from JSON users file
def load_users(input):
    print("Inspecting:", input)
    
    print("-- Loading Users information")
    with open(os.path.join(input, "users.json"), encoding="utf8") as f:
        users = {u["id"]: (u["id"], u["name"], "<@"+u["id"]+">", "@"+u["name"]) for u in json.load(f)}
    print("Users loaded", len(users))
    return users


def replace_userid_names_in_json(input, users):
    print("Processing:", input)

    # patterns to search
    re_text = re.compile("^        \"text\": ")
    re_user = re.compile("<@(W[0-9A-Z]{8})>")

    # scan on slack-export folder for subfolders (channels, groups, DMs)
    print("Inspecting subfolders")
    subfolders = [ f.path for f in os.scandir(input) if f.is_dir() ]

    for group_folder in subfolders:
        # only process json files = messages files
        print("-- Processing:", group_folder)
        json_files = [ os.path.join(group_folder, f.name) for f in os.scandir(group_folder) if (f.is_file() and f.name.endswith(".json")) ]
        for json_file in json_files:
            print("-- -- JSON:", json_file)
            changes = 0
            # find and replace in json files
            for _, line in enumerate(fileinput.input(json_file, inplace=True)):
                # User ID will only be replaced on "text" fields
                if (re_text.match(line) != None):
                    # for every USER ID, replace with its corresponding NAME
                    for match_user in re_user.finditer(line):
                        # if same USER ID has more than one occurrence, it is expected to try to replace it more than once
                        line = line.replace(users[match_user.group(1)][2], users[match_user.group(1)][3])
                        changes+= 1

                # Printing unmodified and modified lines
                print(line, end="")
            # 
            print("Changes:", changes)
        print(end="\n")
    print(end="\n")


# MAIN
if (__name__ == "__main__"):
    # Args
    parser = argparse.ArgumentParser(description="Replace User ID with Name in JSON files exported by slack-export")
    parser.add_argument('--input', required=True, help="Export folder created by slack-export")
    args = parser.parse_args()
    
    users = load_users(args.input)
    
    replace_userid_names_in_json(args.input, users)
