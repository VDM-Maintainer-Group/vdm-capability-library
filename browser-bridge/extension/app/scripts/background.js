
let port = browser.runtime.connectNative('org.vdm.browser_bridge');
console.log(port)

browser.windows.onCreated.addListener((window) => {
    if (window.type=='normal') {
        res = {'w_id':window.id, 'res':'event', 'name':'window_created'}
        port.postMessage( res )
    }
});

browser.windows.onRemoved.addListener((windowId) => {
    res = {'w_id':windowId, 'res':'event', 'name':'window_removed'}
    port.postMessage( res )
});

function post_message(w_id, ret) {
    res = {'w_id':w_id, 'res':ret};
    port.postMessage( res );
}

port.onMessage.addListener((msg) => {
    let w_id = msg['w_id'];

    switch(msg['req']) {
        case 'sync':
            browser.windows.getAll({ windowTypes: ["normal"] })
            .then((windows) => {
                ret = windows.map( w => w.id );
                post_message(w_id, ret);
            }, (err) => {
                console.error(err);
                post_message(w_id, -1);
            });
            break;

        case 'save':
            browser.tabs.query({ 'windowId':w_id })
            .then((tabs) => {
                post_message(w_id, tabs);
            }, (err) => {
                console.error(err)
                post_message(w_id, -1);
            })
            break;
        case 'resume':
            browser.tabs.query({'windowId':w_id})
            .then((tabs) => {
                // create new tabs
                msg['stat'].map((stat) => {
                    browser.tabs.create({'url':stat['url']})
                })
                .then((_) => {
                    // close old tabs
                    let id_tabs = tabs.map( x => x['id'] );
                    browser.tabs.remove(id_tabs)
                    .then(()=>{
                        post_message(w_id, ret);
                    }, (err) => {
                        console.error(err)
                        post_message(w_id, -1);
                    });
                }, (err) => {
                    console.error(err)
                    post_message(w_id, -1);
                });
            });
            break;
        case 'new':
            let stat = JSON.parse( msg['stat'] )
            let x,y,h,w = stat['xyhw']
            browser.windows.create({
                'incognito':stat['incognito'], 'url':stat['url'],
                'left':x, 'top':y, 'height':h, 'width':w
            }, (_) => {
                post_message(w_id, 0);
            }, (err) => {
                console.error(err)
                post_message(w_id, -1);
            });
            break;
        case 'close':
            browser.windows.remove(w_id)
            .then(() => {
                post_message(w_id, 0);
            }, (err) => {
                console.error(err)
            })
            break;
        
        case 'open_temp':
            tab_name = msg['name']
            browser.tabs.create({
                'title':tab_name, 'discarded':true, 'url':'/pages/popup.html'
            })
            .then((tab) => {
                post_message(w_id, tab.id);
            }, (err) => {
                console.error(err)
                post_message(w_id, -1);
            });
            break;
        case 'close_temp':
            tab_id = msg['t_id']
            browser.tabs.remove( tab_id )
            .then(() => {
                post_message(w_id, 0);
            }, (err) => {
                console.error(err)
                post_message(w_id, -1);
            });
            break;
    };
});
