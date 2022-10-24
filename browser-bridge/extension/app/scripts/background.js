function encrypt_message(msg, callback) {
    browser.storage.sync.get("digest_passwd")
    .then((items) => {
        let pwd = ("digest_passwd" in items)? items["digest_passwd"] : "browser-bridge-undefined";
        require(["./bower_components/crypto-js/aes"], (AES) => {
            let enc_msg = AES.encrypt(msg, pwd).toString();
            callback(enc_msg);
        });
    })
}

function decrypt_message(msg, callback) {
    browser.storage.sync.get("digest_passwd")
    .then((items) => {
        let pwd = ("digest_passwd" in items)? items["digest_passwd"] : "browser-bridge-undefined";
        require(["./bower_components/crypto-js/aes", "./bower_components/crypto-js/enc-utf8"], (AES, enc_Utf8) => {
            let dec_bytes = AES.decrypt(msg, pwd);
            let dec_msg = dec_bytes.toString( enc_Utf8 );
            callback(dec_msg);
        });
    })
}

// ------------------------------------------------------------- //

function get_all_windows(callback) {
    browser.windows.getAll({ windowTypes: ["normal"] })
    .then((windows) => {
        ret = windows.map( w => w.id );
        callback( ret );
    }, (err) => {
        console.error(err);
        callback( {} );
    });
}

function get_all_window_tabs(w_id, callback) {
    browser.windows.get(w_id)
    .then((window) => {
        let incognito = window.incognito;

        browser.tabs.query({ "windowId":w_id })
        .then((tabs) => {
            let r_tabs = tabs.map((stat) => {return {
                "url":stat.url, "active":stat.active,
                // "title": x.title, "pinned": x.pinned
            }});
            let msg = JSON.stringify({ "incognito":incognito, "tabs":r_tabs });
            encrypt_message(msg, (enc_msg) => {
                callback( enc_msg );
            });
        }, (err) => {
            console.error(err);
            callback( "" );
        })
    });
}

function close_window(w_id, callback) {
    browser.windows.remove(w_id)
    .then(() => {
        callback( 0 );
    }, (err) => {
        console.error(err);
        callback( -1 )
    });
}

function new_window_tabs(stat, callback) {
    let incognito = stat["incognito"];
    let urls = stat["tabs"].map( tab => tab.url );

    browser.windows.create({
        "incognito":incognito, "url":urls,
    }, (_) => {
        callback( 0 );
    }, (err) => {
        console.error(err);
        callback( -1 );
    });
}

function replace_window_tabs(w_id, stat, callback) {
    let incognito = stat["incognito"];
    let r_tabs = stat["tabs"];

    browser.windows.get(w_id)
    .then((window) => {
        if (window.incognito!=incognito) {
            new_window_tabs(stat, callback);
            browser.windows.remove(w_id).then(
                ()=>{}, (_)=>{}
            );
        }
        else {
            browser.tabs.query({"windowId":w_id})
            .then((old_tabs) => {
                let id_tabs = old_tabs.map( x => x["id"] );
                // create new tabs
                r_tabs.map((tab) => {
                    browser.tabs.create({
                        "url":tab.url, "active":tab.active
                    }).then((_)=>{}, (_)=>{});
                });
                // close old tabs
                browser.tabs.remove(id_tabs)
                .then(() => {
                    callback( 0 );
                }, (err) => {
                    console.error(err);
                    callback( -1 );
                });
            })
        }
    })
}

function open_temp(name, callback) {
    browser.tabs.create({
        "active":true, "url":`/pages/transition.html?${name}`
    })
    .then((tab) => {
        callback( tab.id );
    }, (err) => {
        console.error(err);
        callback( -1 );
    });
}

function close_temp(t_id, callback) {
    browser.tabs.remove( t_id )
    .then(() => {
        callback( 0 );
    }, (err) => {
        console.error(err);
        callback( -1 );
    });
}

let ops = {
    "sync": get_all_windows,
    "save": get_all_window_tabs,
    "close": close_window,

    "new": create_window,
    "resume": replace_window_tabs,

    "open_temp": open_temp,
    "close_temp": close_temp
};

// ------------------------------------------------------------- //
let port = browser.runtime.connectNative("org.vdm.browser_bridge");

browser.tabs.onUpdated.addListener(async (tabId) => {
    browser.pageAction.show(tabId)
});

browser.windows.onCreated.addListener((window) => {
    if (window.type=="normal") {
        res = {"w_id":window.id, "res":"event", "name":"window_created"}
        port.postMessage( res )
    }
});

browser.windows.onRemoved.addListener((windowId) => {
    res = {"w_id":windowId, "res":"event", "name":"window_removed"}
    port.postMessage( res )
});

port.onMessage.addListener((msg) => {
    let post_callback = (ret) => {
        port.postMessage({ "w_id":msg["w_id"], "res":ret });
    };

    switch (msg["req"]) {
        case "sync":
            ops.sync(post_callback); break;
        case "save":
            ops.save(msg["w_id"], post_callback); break;
        case "close":
            ops.close(msg["w_id"], post_callback); break;
        case "resume":
            decrypt_message(msg["stat"], (stat) => {
                ops.resume(msg["w_id"], stat, post_callback);
            }); break;
        case "new":
            decrypt_message(msg["stat"], (stat) => {
                ops.new(stat, post_callback);
            }); break;
        case "open_temp":
            ops.open_temp(msg["name"], post_callback); break;
        case "close_temp":
            ops.close_temp(msg["t_id"], post_callback); break;
    }
});
