#!/usr/bin/env python3
from time import sleep
from sys import stdin, stdout
import struct, json, socket

def nm_recv():
    RAW_LEN    = struct.calcsize('@I')
    raw_len = stdin.buffer.read(RAW_LEN)
    buf_len = struct.unpack("@I", raw_len)[0]
    buf = stdin.buffer.read(buf_len).decode('utf-8')
    return json.loads(buf)

def nm_send(msg):
    buf     = json.dumps(msg).encode('utf-8')
    buf_len = struct.pack('@I', len(buf))

    stdout.buffer.write(buf_len)
    stdout.buffer.write(buf)
    stdout.flush()
    pass

def sync_ctrl(ctrl_msg):
    nm_send(ctrl_msg)
    return nm_recv()

def main():
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd.connect(('', 11112))
    while True:
        split_try = fd.recv(4096).decode('utf-8').split()

        if len(split_try) == 1:
            cmd = split_try[0]
        else:
            cmd, data = split_try
        ctrl_msg = {'cmd': cmd}

        if cmd=='save':
            res = sync_ctrl(ctrl_msg)
            fd.send(json.dumps(res).encode('utf-8'))
            pass
        elif cmd=='load':
            #TODO:
            pass
        elif cmd=='close':
            #TODO:
            pass
        else:
            pass
        pass
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
    finally:
        pass
