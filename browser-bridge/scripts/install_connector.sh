#!/usr/bin/env bash

chmod +x ../connector/connector.py
mkdir -p /opt/browser-bridge
cp ../connector/connector.py /opt/browser-bridge

# for chrome
# mkdir -p ~/.config/google-chrome/NativeMessagingHosts
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_chrome.py
# cp ../connector/org.vdm.browser_bridge.chrome.json ~/.config/google-chrome/NativeMessagingHosts/org.vdm.browser_bridge.json
mkdir -p /etc/opt/chrome/native-messaging-hosts
cp ../connector/org.vdm.browser_bridge.chrome.json /etc/opt/chrome/native-messaging-hosts/org.vdm.browser_bridge.json

# for firefox
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_firefox.py
# mkdir -p ~/.mozilla/native-messaging-hosts
# cp ../connector/org.vdm.browser_bridge.firefox.json ~/.mozilla/native-messaging-hosts/org.vdm.browser_bridge.json
mkdir -p /usr/lib/mozilla/native-messaging-hosts
cp ../connector/org.vdm.browser_bridge.firefox.json /usr/lib/mozilla/native-messaging-hosts/org.vdm.browser_bridge.json

# for microsoft edge
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_edge.py
# mkdir -p ~/.config/microsoft-edge/NativeMessagingHosts
# cp ../connector/org.vdm.browser_bridge.edge.json ~/.config/microsoft-edge/NativeMessagingHosts/org.vdm.browser_bridge.json
mkdir -p /etc/opt/edge/native-messaging-hosts
cp ../connector/org.vdm.browser_bridge.edge.json /etc/opt/edge/native-messaging-hosts/org.vdm.browser_bridge.json
