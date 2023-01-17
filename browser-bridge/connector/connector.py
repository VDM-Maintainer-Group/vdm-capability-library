#!/usr/bin/env python3
import asyncio, threading
from queue import Queue
import struct, json, random, string
from pathlib import Path
from sys import stdin, stdout
import dbus, dbus.service, dbus.mainloop.glib
from gi.repository import GLib

from pyvdm.interface import CapabilityLibrary
xm = CapabilityLibrary.CapabilityHandleLocal('x11-manager')

# import logging, traceback
# logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG, filename='/tmp/browser-bridge.log', filemode='w')

async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, stdout)
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return (reader, writer)

def retry_with_timeout(lamb_fn, timeout=1):
    import time
    _now = time.time()
    ret = lamb_fn()
    while not ret and time.time()-_now<timeout:
        ret = lamb_fn()
        time.sleep(0.1)
    return ret

class BrowserConnector:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        pass

    async def nm_recv(self) -> dict:
        RAW_LEN = struct.calcsize('@I')
        raw_len = await self.reader.read(RAW_LEN)
        buf_len = struct.unpack("@I", raw_len)[0]
        buf = ( await self.reader.read(buf_len) ).decode('utf-8')
        return json.loads(buf)

    async def nm_send(self, msg: dict):
        buf     = json.dumps(msg).encode('utf-8')
        buf_len = struct.pack('@I', len(buf))
        self.writer.write(buf_len)
        self.writer.write(buf)
        await self.writer.drain()
        pass

    async def nm_request_sync(self, msg:dict) -> dict:
        await self.nm_send(msg)
        ret = await self.nm_recv()
        return ret
    pass

class BrowserWindowInterface(dbus.service.Object):
    def __init__(self, name, w_id, tx_q, rx_q) -> None:
        self.name, self.w_id = name, w_id
        self.tx_q, self.rx_q = tx_q, rx_q
        ##
        self.xid = 0
        self.unique = ''.join(random.choices(string.ascii_letters, k=5))
        ##
        bus_name = f'org.VDMCompatible.{self.name}.{self.unique}'
        conn = dbus.service.BusName(bus_name, bus=dbus.SessionBus(private=True))
        super().__init__(conn, '/')
        pass

    def sync_ctrl(self, cmd):
        self.tx_q.put(cmd)
        ret = self.rx_q.get()
        return ret

    def set_xid(self):
        if hasattr(self, 'xid') and self.xid:
            return
        #
        temp_name = f'{self.name}-{self.unique}'
        t_id = self.sync_ctrl({'req':'open_temp', 'w_id':self.w_id, 'name':temp_name})
        try:
            _lamb_fn = lambda: xm.get_windows_by_name(temp_name)
            _window = retry_with_timeout(_lamb_fn)[0]
            self.xid = _window['xid']
        except:
            self.xid = 0
        finally:
            self.sync_ctrl({'req':'close_temp', 'w_id':self.w_id, 't_id':t_id})
        # logging.info(f'xid update: {self.xid}')
        pass

    @dbus.service.method(dbus_interface='org.VDMCompatible.src',
                        out_signature='s')
    def Save(self) -> str:
        ret = self.sync_ctrl({'req':'save', 'w_id':self.w_id})
        self.set_xid()
        return ret
    
    @dbus.service.method(dbus_interface='org.VDMCompatible.src',
                        in_signature='sb')
    def Resume(self, stat:str, new:bool):
        _req = 'new' if new else 'resume'
        self.sync_ctrl({'req':_req, 'w_id':self.w_id, 'stat':stat})
        pass

    @dbus.service.method(dbus_interface='org.VDMCompatible.src')
    def Close(self):
        self.sync_ctrl({'req':'close', 'w_id':self.w_id})
        pass

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name=='org.VDMCompatible.src' and property_name=='xid':
            return self.xid
        else:
            raise dbus.exceptions.DBusException('com.example.UnknownInterface',
                    'interface %s not found.'%interface_name)
        pass

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        if interface_name == 'org.VDMCompatible.src':
            return { 'xid' : self.xid }
        else:
            raise dbus.exceptions.DBusException('com.example.UnknownInterface',
                    'interface %s not found.'%interface_name)
        pass
    pass

def start_glib_thread():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    GLib.MainLoop().run()

async def handle_event(browser_name):
    (reader, writer) = await connect_stdin_stdout()
    connector = BrowserConnector(reader, writer)
    recv_queue = Queue()
    ## sync existing windows
    ifaces = dict()
    res = await connector.nm_request_sync({'req':'sync', 'w_id':0})
    for w_id in res['res']:
        tx_q = Queue()
        _iface = BrowserWindowInterface(browser_name, w_id, recv_queue, tx_q)
        ifaces[ w_id ] = {
            'iface': _iface,
            'tx_q': tx_q
        }
    ## handling for two creators
    while True:
        ## handle events from stdin (on main thread)
        try:
            res = await asyncio.wait_for( connector.nm_recv(), timeout=0.01 )
            res_type, w_id = res['res'], res['w_id']
            if res_type=='event':
                if res['name']=='window_created':
                    tx_q = Queue()
                    _iface = BrowserWindowInterface(browser_name, w_id, recv_queue, tx_q)
                    ifaces[ w_id ] = {
                        'iface': _iface,
                        'tx_q': tx_q
                    }
                elif res['name']=='window_removed':
                    _val = ifaces.pop( w_id )
                    _val['iface'].remove_from_connection()
                    pass
            else:
                ifaces[ w_id ]['tx_q'].put( res['res'] )
        except asyncio.TimeoutError:
            pass
        except:
            # logging.error( traceback.format_exc() )
            exit()
        ## handle events from d-bus (on another thread)
        try:
            req = recv_queue.get_nowait()
            await connector.nm_send( req )
        except:
            pass
        ## obey the event loop on current thread
        await asyncio.sleep(0)
    pass

def main():
    try:
        browser_name = Path(__file__).stem[ len('connector_'): ]
    except:
        browser_name = 'test'
    threading.Thread(target=start_glib_thread, daemon=True, args=()).start()
    asyncio.run( handle_event(browser_name) )
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
    finally:
        pass
