
chrome.runtime.onInstalled.addListener(function() {
    var port = chrome.runtime.connectNative('org.vdm.chrome');

    port.onMessage.addListener(function(msg){
        console.log(msg)
        switch (msg['cmd']) {
            case 'save':
                chrome.tabs.query({}, function(results) {
                    res = {}
                    results.forEach(function(tab) {
                        _item = {'index': tab.index, 'title':tab.title, 'url': tab.url}
                        if (Array.isArray(res[tab.windowId])) {
                            res[tab.windowId].push(_item);
                        }
                        else {
                            res[tab.windowId] = [_item]
                        }
                    });
                    port.postMessage( JSON.stringify(res) );
                });
                break;
            case 'load':
                //TODO:
                break;
            case 'close':
                //TODO:
                break;
            default:
                break;
        }
    });

    port.onDisconnect.addListener(function(){
        console.log("VDM-Chrome Host Disconnected.")
    });
    
    // port.postMessage("hello");
});
