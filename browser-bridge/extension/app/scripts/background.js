browser.runtime.onInstalled.addListener((details) => {
  console.log('previousVersion', details.previousVersion)
})

// browser.tabs.onUpdated.addListener(async (tabId) => {
//   browser.pageAction.show(tabId)
// })

let port = browser.runtime.connectNative('org.vdm.browser_bridge');
console.log(port)

port.onMessage.addListener((msg) => {
  switch(msg['req']) {
    case 'dump':
      browser.tabs.query({}, (results) => {
        res = {}
        results.forEach(tab => {
          _item = {'index': tab.index, 'title':tab.title, 'url': tab.url}
          if (Array.isArray(res[tab.windowId])) {
            res[tab.windowId].push(_item)
          }
          else {
            res[tab.windowId] = [_item]
          }
        });
        port.postMessage( JSON.stringify(res) );
      })
      break;
    case 'resume':
      break;
    case 'exist':
      break;
    case 'open_temp':
      break;
    case 'close_temp':
      break;
    default:
      break;
  }
})
