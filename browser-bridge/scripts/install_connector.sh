#!/usr/bin/env bash

chmod +x ../connector/connector.py
sudo mkdir -p /opt/browser-bridge
sudo cp ../connector/connector.py /opt/browser-bridge

# for chrome
# mkdir -p ~/.config/google-chrome/NativeMessagingHosts
sudo ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_chrome.py
# cp ../connector/org.vdm.browser_bridge.chrome.json ~/.config/google-chrome/NativeMessagingHosts/org.vdm.browser_bridge.json
sudo mkdir -p /etc/opt/chrome/native-messaging-hosts
sudo cp ../connector/org.vdm.browser_bridge.chrome.json /etc/opt/chrome/native-messaging-hosts/org.vdm.browser_bridge.json

# for firefox
sudo ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_firefox.py
# mkdir -p ~/.mozilla/native-messaging-hosts
# cp ../connector/org.vdm.browser_bridge.firefox.json ~/.mozilla/native-messaging-hosts/org.vdm.browser_bridge.json
sudo mkdir -p /usr/lib/mozilla/native-messaging-hosts
sudo cp ../connector/org.vdm.browser_bridge.firefox.json /usr/lib/mozilla/native-messaging-hosts/org.vdm.browser_bridge.json

# for microsoft edge
sudo ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_edge.py
# mkdir -p ~/.config/microsoft-edge/NativeMessagingHosts
# cp ../connector/org.vdm.browser_bridge.edge.json ~/.config/microsoft-edge/NativeMessagingHosts/org.vdm.browser_bridge.json
sudo mkdir -p /etc/opt/edge/native-messaging-hosts
sudo cp ../connector/org.vdm.browser_bridge.edge.json /etc/opt/edge/native-messaging-hosts/org.vdm.browser_bridge.json
