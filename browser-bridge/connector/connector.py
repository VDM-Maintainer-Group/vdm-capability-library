#!/usr/bin/env python3

import struct, json, random, string
from pathlib import Path
from sys import stdin, stdout
from time import sleep
import dbus, dbus.service, dbus.mainloop.glib
from gi.repository import GLib

FILE_NAME_MAP = {
    'connector_chrome': 'google-chrome',
    'connector_firefox': 'firefox-esr',
    'connector_edge': 'microsoft-edge',
}

class BrowserConnector:
    def __init__(self, name):
        self.name = name
        pass

    @staticmethod
    def __nm_recv() -> dict:
        RAW_LEN = struct.calcsize('@I')
        raw_len = stdin.buffer.read(RAW_LEN)
        buf_len = struct.unpack("@I", raw_len)[0]
        buf = stdin.buffer.read(buf_len).decode('utf-8')
        return json.loads(buf)

    @staticmethod
    def __nm_send(msg: dict):
        buf     = json.dumps(msg).encode('utf-8')
        buf_len = struct.pack('@I', len(buf))
        stdout.buffer.write(buf_len)
        stdout.buffer.write(buf)
        stdout.flush()
        pass

    def nm_request_sync(self, cmd:str) -> str:
        ctrl_msg = {'req':cmd}
        self.__nm_send(ctrl_msg)
        return self.__nm_recv()
    
    def open_temp_tabs(self):
        pass

    def close_temp_tabs(self):
        pass

    def dump_tabs(self):
        return self.nm_request_sync('dump')

    def resume_tabs(self):
        pass

    pass

class BrowserBridgeInterface(dbus.service.Object):
    def __init__(self, name) -> None:
        self.name = name
        self.unique = ''.join(random.choices(string.ascii_letters, k=5))
        bus_name = f'org.VDMCompatible.{self.name}.{self.unique}'
        ##
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        conn = dbus.service.BusName(bus_name, bus=dbus.SessionBus())
        super().__init__(conn, '/')
        pass

    @dbus.service.method(dbus_interface='org.VDMCompatible.src',
                        out_signature='s')
    def Save(self) -> str:
        ret = BrowserConnector('test').dump_tabs()
        return json.dumps(ret)
    
    @dbus.service.method(dbus_interface='org.VDMCompatible.src',
                        in_signature='s')
    def Resume(self, stat:str):
        pass

    @dbus.service.method(dbus_interface='org.VDMCompatible.src')
    def Close(self):
        pass

    pass

def main():
    try:
        browser_name = FILE_NAME_MAP[ Path(__file__).stem ]
    except:
        browser_name = 'test'
    BrowserBridgeInterface(browser_name)
    GLib.MainLoop().run()
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
    finally:
        pass
