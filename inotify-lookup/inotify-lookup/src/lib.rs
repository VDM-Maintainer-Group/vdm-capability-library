use neli::socket::NlSocketHandle;

pub enum InotifyOp {
    InotifyReqAdd = 0x01,
    InotifyReqRm  = 0x02,
    InotifyReqDump= 0x04,
}
// const MAX_DUMP_LEN: usize = 1000; // maximum number of received dump

mod _priv {
    use super::{InotifyOp,};
    use std::process::id as getpid;
    use neli::{
        consts::{nl::*, socket::*},
        err::NlError,
        nl::{Nlmsghdr, NlPayload},
        socket::NlSocketHandle,
    };

    #[allow(dead_code)] //Rust lint open issue, #47133
    const NETLINK_USER: i32 = 31;   // (fixed) netlink specific magic number
    const MAX_NAME_LEN: usize = 10; // FIXME:1024 (fixed) maximum length of app name
    // const MAX_PATH_LEN: usize = 4096; // (fixed) maximum length of inode pathname
    #[repr(C,packed)]
    struct ReqMessage {
        #[allow(dead_code)] //op never read in "safe" mode
        op : libc::c_int,
        comm_name: [u8; MAX_NAME_LEN]
    }

    //Reference: https://stackoverflow.com/questions/28127165/how-to-convert-struct-to-u8
    unsafe fn any_as_u8_slice<T: Sized>(p: &T) -> &[u8] {
        ::std::slice::from_raw_parts(
            (p as *const T) as *const u8,
            ::std::mem::size_of::<T>(),
        )
    }

    pub fn get_socket() -> Result<NlSocketHandle, NlError> {
        let socket = NlSocketHandle::connect(
            NlFamily::UnrecognizedVariant(NETLINK_USER), Some(getpid()), &[])?;
        Ok(socket)
    }

    pub fn send_request(mut socket:NlSocketHandle, op:InotifyOp, name:&str) -> Result<NlSocketHandle,NlError> {
        let mut message = ReqMessage{
            op : op as libc::c_int,
            comm_name : [0 as u8; MAX_NAME_LEN]
        };
        
        for (i, x) in name.as_bytes().iter().enumerate() {
            message.comm_name[i] = *x;
        }
        let message = unsafe{ any_as_u8_slice(&message) };
        
        let nlhdr = {
            let len = None;
            let nl_type = 0 as u16;
            let flags = NlmFFlags::new(&[]);
            let seq = None;
            let pid = Some(getpid());
            let payload = NlPayload::Payload(message);
            Nlmsghdr::new(len, nl_type, flags, seq, pid, payload)
        };
        socket.send(nlhdr)?;

        Ok(socket)
    }

    pub fn recv_message(mut socket:NlSocketHandle) -> Result<Vec<String>,()> {
        let mut result = Vec::<String>::new();

        while let Ok(Some(packet)) = socket.recv::<Nlmsg, Vec<u8>>() {
            match packet.nl_type {
                Nlmsg::Done => break,
                _ => {
                    let _content = packet.nl_payload.get_payload().unwrap();
                    let _content = std::str::from_utf8(_content).unwrap();
                    result.push( String::from(_content) );
                }
            }
        }

        Ok(result)
    }
}

fn inotify_send_request(op:InotifyOp, name:String) -> Result<NlSocketHandle, ()> {
    if let Ok(socket) = _priv::get_socket() {
        match _priv::send_request(socket, op, &name) {
            Ok(socket) => Ok(socket),
            Err(_) => Err(())
        }
    }
    else {
        Err(())
    }
}

use serde_wrapper::jsonify;

#[no_mangle]#[jsonify]
pub fn register(name: String) -> isize {
    match inotify_send_request(InotifyOp::InotifyReqAdd, name) {
        Ok(_) => 0,
        Err(_) => -1
    }
}

#[no_mangle]#[jsonify]
pub fn unregister(name: String) -> isize {
    match inotify_send_request(InotifyOp::InotifyReqRm, name) {
        Ok(_) => 0,
        Err(_) => -1
    }
}

#[no_mangle]#[jsonify]
pub fn dump(name: String) -> Vec<String> {
    match inotify_send_request(InotifyOp::InotifyReqDump, name) {
        Err(_) => Vec::<String>::new(),
        Ok(socket) => {
            if let Ok(result) = _priv::recv_message(socket) {
                result
            }
            else {
                Vec::<String>::new()
            }
        }
    }
}

#[test]
fn run_test() -> Result<(), std::io::Error> {
    let app_name = serde_json::to_string("code").unwrap();
    let args=format!( "{{ \"name\":{} }}", app_name );

    println!("register: {}", register( args.clone() ));
    println!("dump: {:?}", dump( args.clone() ));
    //println!("unregister: {}", unregister( app_name.clone() ));

    Ok(())
}
