browser.runtime.onInstalled.addListener((details) => {
  console.log('previousVersion', details.previousVersion)
})

let port = browser.runtime.connectNative('org.vdm.browser_bridge');
console.log(port)

browser.windows.onCreated.addListener((window) => {
    if (window.type=='normal') {
        res = {'w_id':window.id, 'res':'event', 'name':'window_created'}
        port.postMessage( JSON.stringify(res) )
    }
});

browser.windows.onRemoved.addListener((window) => {
    if (window.type=='normal') {
        res = {'w_id':window.id, 'res':'event', 'name':'window_removed'}
        port.postMessage( JSON.stringify(res) )
    }
});

port.onMessage.addListener((msg) => {
    let w_id = msg['w_id'];
    let ret = -1;

    switch(msg['req']) {
        case 'save':
            browser.tabs.query({ 'windowId':w_id })
            .then((tabs) => {
                ret = tabs
            }, (err) => {
                console.log(err)
            })
            break;
        case 'resume':
            let stat = JSON.parse( msg['stat'] )
            let (x,y,h,w) = stat['xyhw']
            browser.windows.update(w_id, {
                'incognito':stat['incognito'], 'url':stat['url'],
                'left':x, 'top':y, 'height':h, 'width':w
            }, (details) => {
                ret = 0
            }, (err) => {
                console.log(err)
            });
            break;
        case 'close':
            browser.windows.remove(w_id)
            .then(() => {
                ret = 0
            }, (err) => {
                console.log(err)
            })
            break;
        
        case 'open_temp':
            tab_name = msg['name']
            browser.tabs.create({
                'title':tab_name, 'discarded':true, 'active':true
            })
            .then((tab) => {
                ret = tab.id
            }, (err) => {
                console.log(err)
            });
            break;
        //
        case 'close_temp':
            tab_id = msg['t_id']
            browser.tabs.remove( tab_id )
            .then(() => {
                ret = 0
            }, (err) => {
                console.log(err)
            });
            break;
    };

    res = {'w_id':w_id, 'res':ret}
    postMessage.postMessage( JSON.stringify(res) )
});
