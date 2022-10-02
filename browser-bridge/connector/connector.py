#!/usr/bin/env python3
import asyncio, threading
from queue import Queue
import struct, json, random, string
from pathlib import Path
from sys import stdin, stdout
from time import sleep
import dbus, dbus.service, dbus.mainloop.glib
from gi.repository import GLib

from pyvdm.interface import CapabilityLibrary
xm = CapabilityLibrary.CapabilityHandleLocal('x11-manager')

FILE_NAME_MAP = {
    'connector_chrome': 'google-chrome',
    'connector_firefox': 'firefox-esr',
    'connector_edge': 'microsoft-edge',
}

async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, stdout)
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return (reader, writer)

class BrowserConnector:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        pass

    async def __nm_recv(self) -> dict:
        RAW_LEN = struct.calcsize('@I')
        raw_len = await self.reader.read(RAW_LEN)
        buf_len = struct.unpack("@I", raw_len)[0]
        buf = await self.reader.read(buf_len).decode('utf-8')
        return json.loads(buf)

    async def __nm_send(self, msg: dict):
        buf     = json.dumps(msg).encode('utf-8')
        buf_len = struct.pack('@I', len(buf))
        self.writer.write(buf_len)
        self.writer.write(buf)
        await self.writer.drain()
        pass

    async def nm_request_sync(self, cmd:str) -> str:
        ctrl_msg = {'req':cmd}
        await self.__nm_send(ctrl_msg)
        return await self.__nm_recv()

    pass

class BrowserWindowInterface(dbus.service.Object):
    def __init__(self, name, w_id, tx_q, rx_q) -> None:
        self.name, self.w_id = name, w_id
        self.tx_q, self.rx_q = tx_q, rx_q
        ##
        self.xid = 0
        self.set_xid()
        self.unique = ''.join(random.choices(string.ascii_letters, k=5))
        ##
        bus_name = f'org.VDMCompatible.{self.name}.{self.unique}'
        conn = dbus.service.BusName(bus_name, bus=dbus.SessionBus())
        super().__init__(conn, '/')
        pass

    def sync_ctrl(self, cmd):
        self.tx_q.put(cmd)
        ret = self.rx_q.get() #blocking
        return json.dumps(ret)

    def set_xid(self):
        temp_name = f'{self.name}-{self.unique}'
        ret = self.sync_ctrl({'req':'open_temp', 'w_id':self.w_id, 'name':temp_name})
        t_id = ret['t_id']
        try:
            _window = xm.get_windows_by_name(temp_name)[0]
            self.xid = _window['xid']
        except:
            self.xid = 0
        finally:
            self.sync_ctrl({'req':'close_temp', 'w_id':self.w_id, 't_id':t_id})
        pass

    @dbus.service.method(dbus_interface='org.VDMCompatible.src',
                        out_signature='s')
    def Save(self) -> str:
        ret = self.sync_ctrl({'req':'save', 'w_id':self.w_id})
        return ret
    
    @dbus.service.method(dbus_interface='org.VDMCompatible.src',
                        in_signature='ss')
    def Resume(self, stat:str, new:bool):
        if new:
            _req = 'new'
        else:
            _req = 'resume'
        ret = self.sync_ctrl({'req':_req, 'w_id':self.w_id, 'stat':stat})
        return ret

    @dbus.service.method(dbus_interface='org.VDMCompatible.src')
    def Close(self):
        self.sync_ctrl({'req':'close', 'w_id':self.w_id})
        pass

    @dbus.service.method(interface=dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name=='org.VDMCompatible.src' and property_name=='xid':
            return self.xid
        else:
            raise dbus.exceptions.DBusException('com.example.UnknownInterface',
                    'interface %s not found.'%interface_name)
        pass

    @dbus.service.method(interface=dbus.PROPERTIES_IFACE,
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
    ##
    while True:
        #TODO: handle events
        ##
        try:
            req = recv_queue.get_nowait()
        except:
            pass

        await asyncio.sleep(0)
    pass

def main():
    try:
        browser_name = FILE_NAME_MAP[ Path(__file__).stem ]
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
