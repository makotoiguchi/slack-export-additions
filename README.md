# slack-export-additions

## Description
Complement slack-export files by adjusting usernames, downloading the attachments and pointing slack links to a new file server.


## Dependencies
* [slack-export](https://github.com/zach-snell/slack-export/) - we use the exported files created by slack export as an input for the scripts
* [slack-export-viewer](https://github.com/hfaran/slack-export-viewer) - the adjusted files are viewed using slack-export-viewer
* [Slack legacy token](https://api.slack.com/legacy/custom-integrations/legacy-tokens) - Slack token to use Slack API


## Usage

### Request Slack Token
Request your [Slack legacy token](https://api.slack.com/legacy/custom-integrations/legacy-tokens)

### Export Slack info
Use [slack-export](https://github.com/zach-snell/slack-export/) to export the information you want (public and private channels, group chat and/or DMs).
Exported folder name pattern is: `YYYYMMDD-HHMMSS-slack_export` 

### Adjusting user names
The first script will replace user **Ids** with the corresponding **Names**.
```shell
./adjust_userid_names.py --input YYYYMMDD-HHMMSS-slack_export
```
Changes are made "in place" on the JSON files.

### Download attachments
This script inspects JSON files and downloads all the _attachment_ files.
```shell
./fetch_attachments.py --token xoxp-0123456789-... --input YYYYMMDD-HHMMSS-slack_export
```
You will need your slack token for this script.
Files will be written in `files` folder inside `YYYYMMDD-HHMMSS-slack_export`

### Replace links
This last step is to adapt the exported JSON files to point all attachment links to a file server you would like to use.
```shell
./replace_attachment_links.py --input YYYYMMDD-HHMMSS-slack_export --newurl http://IP:PORT
```
Change `IP` and `PORT` accordingly, as the script will use `newurl` to replace Slack file server address.

### Viewing Slack archive

#### File server
You may use a simple Python HTTP server:
```shell
cd YYYYMMDD-HHMMSS-slack_export/files
python -m http.server PORT --bind IP
```
`IP` and `PORT` should be the same values used on the "replace links" step.

#### slack-export-viewer server
For this step you will need [slack-export-viewer](https://github.com/hfaran/slack-export-viewer).
```
slack-export-viewer -I IP2 -p PORT2 -z YYYYMMDD-HHMMSS-slack_export
```
`PORT2` must be different than `PORT`, in case `IP2` and `IP` are the same.
