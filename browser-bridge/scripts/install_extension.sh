#!/usr/bin/env bash

XPI_ID='browser-bridge@vdm-compatible.org'
CRX_ID='phmlhncfebmikfmkfombdjnkjmkpdjdl'

# for firefox
FIREFOX_FOLDER='/usr/lib/mozilla/extensions'
sudo mkdir -p $FIREFOX_FOLDER/{$XPI_ID}
for x in ../extension/packages/*.xpi; do
    sudo cp "$x" $FIREFOX_FOLDER/{$XPI_ID}/$XPI_ID.xpi
done

# for chrome
CHROME_FOLDER='/opt/google/chrome/extensions'
sudo mkdir -p $CHROME_FOLDER/
sudo cp ../extension/packages/chrome.json $CHROME_FOLDER/$CRX_ID.json
sudo sed -i 's@~@'"$HOME"'@' $CHROME_FOLDER/$CRX_ID.json

# for edge
EDGE_FOLDER='/usr/share/microsoft-edge/extensions'
sudo mkdir -p $EDGE_FOLDER/
sudo cp ../extension/packages/chrome.json $EDGE_FOLDER/$CRX_ID.json
sudo sed -i 's@~@'"$HOME"'@' $EDGE_FOLDER/$CRX_ID.json
