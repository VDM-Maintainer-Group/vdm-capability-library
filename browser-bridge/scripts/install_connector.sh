#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$SCRIPT_DIR/..

chmod +x $ROOT_DIR/connector/connector.py
mkdir -p /opt/browser-bridge
cp $ROOT_DIR/connector/connector.py /opt/browser-bridge

# for chrome
# mkdir -p ~/.config/google-chrome/NativeMessagingHosts
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_chrome.py
# cp $ROOT_DIR/connector/org.vdm.browser_bridge.chrome.json ~/.config/google-chrome/NativeMessagingHosts/org.vdm.browser_bridge.json
mkdir -p /etc/opt/chrome/native-messaging-hosts
cp $ROOT_DIR/connector/org.vdm.browser_bridge.chrome.json /etc/opt/chrome/native-messaging-hosts/org.vdm.browser_bridge.json

# for firefox
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_firefox.py
# mkdir -p ~/.mozilla/native-messaging-hosts
# cp $ROOT_DIR/connector/org.vdm.browser_bridge.firefox.json ~/.mozilla/native-messaging-hosts/org.vdm.browser_bridge.json
mkdir -p /usr/lib/mozilla/native-messaging-hosts
cp $ROOT_DIR/connector/org.vdm.browser_bridge.firefox.json /usr/lib/mozilla/native-messaging-hosts/org.vdm.browser_bridge.json

# for microsoft edge
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_edge.py
# mkdir -p ~/.config/microsoft-edge/NativeMessagingHosts
# cp $ROOT_DIR/connector/org.vdm.browser_bridge.edge.json ~/.config/microsoft-edge/NativeMessagingHosts/org.vdm.browser_bridge.json
mkdir -p /etc/opt/edge/native-messaging-hosts
cp $ROOT_DIR/connector/org.vdm.browser_bridge.edge.json /etc/opt/edge/native-messaging-hosts/org.vdm.browser_bridge.json

# for deepin browser
ln -sf /opt/browser-bridge/connector.py /opt/browser-bridge/connector_deepin.py
mkdir -p /etc/browser/native-messaging-hosts
cp $ROOT_DIR/connector/org.vdm.browser_bridge.deepin.json /etc/browser/native-messaging-hosts/org.vdm.browser_bridge.json
