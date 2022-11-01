#!/usr/bin/env bash

XPI_ID='browser-bridge@vdm-compatible.org'
CRX_ID='phmlhncfebmikfmkfombdjnkjmkpdjdl'

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$SCRIPT_DIR/..

# for firefox
FIREFOX_FOLDER='/usr/lib/mozilla/extensions'
mkdir -p $FIREFOX_FOLDER/{$XPI_ID}
for x in $ROOT_DIR/extension/packages/*.xpi.zip; do
    cp "$x" "${x%.zip}"
    firefox-esr "${x%.zip}" & disown
    break
done

# for chrome
CHROME_FOLDER='/opt/google/chrome/extensions'
mkdir -p $CHROME_FOLDER/
cp $ROOT_DIR/extension/dist/chrome.json $CHROME_FOLDER/$CRX_ID.json

# for edge
EDGE_FOLDER='/usr/share/microsoft-edge/extensions'
mkdir -p $EDGE_FOLDER/
cp $ROOT_DIR/extension/dist/chrome.json $EDGE_FOLDER/$CRX_ID.json
