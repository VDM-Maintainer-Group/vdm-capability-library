function encrypt_message(msg, callback) {
    browser.storage.sync.get('digest_passwd')
    .then((items) => {
        let pwd = ('digest_passwd' in items)? items['digest_passwd'] : 'browser-bridge-undefined';
        require(['./bower_components/crypto-js/aes'], (AES) => {
            let enc_msg = AES.encrypt(msg, pwd).toString();
            callback(enc_msg);
        });
    })
}

function decrypt_message(msg, callback) {
    browser.storage.sync.get('digest_passwd')
    .then((items) => {
        let pwd = ('digest_passwd' in items)? items['digest_passwd'] : 'browser-bridge-undefined';
        require(['./bower_components/crypto-js/aes', './bower_components/crypto-js/enc-utf8'], (AES, enc_Utf8) => {
            let dec_bytes = AES.decrypt(msg, pwd);
            let dec_msg = dec_bytes.toString( enc_Utf8 );
            callback(dec_msg);
        });
    })
}

let port = browser.runtime.connectNative('org.vdm.browser_bridge');
console.log(port)

browser.tabs.onUpdated.addListener(async (tabId) => {
    browser.pageAction.show(tabId)
});

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
                let r_tabs = tabs.map((stat) => {return {
                    'url':stat.url, 'active':stat.active,
                    // 'title': x.title, 'pinned': x.pinned
                }});
                r_tabs = JSON.stringify(r_tabs);
                encrypt_message(r_tabs, (enc_msg) => {
                    post_message(w_id, enc_msg)
                });
            }, (err) => {
                console.error(err)
                post_message(w_id, -1);
            })
            break;
        case 'resume':
            browser.tabs.query({'windowId':w_id})
            .then((old_tabs) => {
                let id_tabs = old_tabs.map( x => x['id'] );
                decrypt_message(msg['stat'], (dec_msg) => {
                    // create new tabs
                    let r_tabs = JSON.parse(dec_msg);
                    r_tabs.map((stat) => {
                        browser.tabs.create({
                            'url':stat.url, 'active':stat.active
                        }).then((_)=>{}, (_)=>{});
                    });
                    // close old tabs
                    browser.tabs.remove(id_tabs)
                    .then(() => {
                        post_message(w_id, 0);
                    }, (err) => {
                        console.error(err)
                        post_message(w_id, -1);
                    });
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
                'active':true, 'url':`/pages/transition.html?${tab_name}`
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
