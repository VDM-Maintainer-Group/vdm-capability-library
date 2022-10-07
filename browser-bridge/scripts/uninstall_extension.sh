#!/usr/bin/env bash
source ./install_extension.sh

# for firefox
sudo rm -rf $FIREFOX_FOLDER/{$XPI_ID}

# for chrome
sudo rm -rf $CHROME_FOLDER/$CRX_ID.json

# for edge
sudo rm -rf $EDGE_FOLDER/$CRX_ID.json
