#!/usr/bin/env bash

XPI_ID='browser-bridge@vdm-compatible.org'
CRX_ID='phmlhncfebmikfmkfombdjnkjmkpdjdl'

# for firefox
FIREFOX_FOLDER='/usr/lib/mozilla/extensions'
mkdir -p $FIREFOX_FOLDER/{$XPI_ID}
for x in ../extension/packages/*.xpi.zip; do
    cp "$x" "${x%.zip}"
    firefox-esr "${x%.zip}" & disown
    break
done

# for chrome
CHROME_FOLDER='/opt/google/chrome/extensions'
mkdir -p $CHROME_FOLDER/
cp ../extension/packages/chrome.json $CHROME_FOLDER/$CRX_ID.json
sed -i 's@~@'"$HOME"'@' $CHROME_FOLDER/$CRX_ID.json

# for edge
EDGE_FOLDER='/usr/share/microsoft-edge/extensions'
mkdir -p $EDGE_FOLDER/
cp ../extension/packages/chrome.json $EDGE_FOLDER/$CRX_ID.json
sed -i 's@~@'"$HOME"'@' $EDGE_FOLDER/$CRX_ID.json
