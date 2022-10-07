#!/usr/bin/env bash

# for firefox

# for chrome
CRX_ID='phmlhncfebmikfmkfombdjnkjmkpdjdl'
sudo mkdir -p /opt/google/chrome/extensions/
sudo cp ../extension/packages/$CRX_ID.json /opt/google/chrome/extensions/
sudo sed -i 's@~@'"$HOME"'@' /opt/google/chrome/extensions/$CRX_ID.json

# for edge
