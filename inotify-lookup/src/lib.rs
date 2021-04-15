use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

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

    pub fn send_request(mut socket:NlSocketHandle, op:InotifyOp, name:&str) -> Result<(),NlError> {
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

        Ok(())
    }

    pub fn recv_message(mut socket:NlSocketHandle) -> Result<Vec<String>,()> {
        let mut result = Vec::<String>::new();
        for next in socket.iter::<String>(true) {
            if let Ok(item) = next {
                let _content = item.get_payload().unwrap();
                println!("{}", _content);
                result.push( String::clone(_content) );
            }
        }
        Ok(result)
    }
}

fn inotify_send_request(op:InotifyOp, name:&str) -> Result<(), ()> {
    if let Ok(socket) = _priv::get_socket() {
        match _priv::send_request(socket, op, name) {
            Ok(_) => Ok(()),
            Err(_) => Err(())
        }
    }
    else {
        Err(())
    }
}

#[pyfunction]
pub fn register(name: &str) -> PyResult<isize> {
    match inotify_send_request(InotifyOp::InotifyReqAdd, name) {
        Ok(_) => Ok(0),
        Err(_) => Ok(-1)
    }
}

#[pyfunction]
pub fn unregister(name: &str) -> PyResult<isize> {
    match inotify_send_request(InotifyOp::InotifyReqRm, name) {
        Ok(_) => Ok(0),
        Err(_) => Ok(-1)
    }
}

#[pyfunction]
pub fn dump(name: &str) -> PyResult<Vec<String>> {
    match inotify_send_request(InotifyOp::InotifyReqDump, name) {
        Err(_) => Ok(Vec::<String>::new()),
        Ok(_) => {
            let socket = _priv::get_socket().unwrap();
            if let Ok(result) = _priv::recv_message(socket) {
                Ok(result)
            }
            else {
                Ok( Vec::<String>::new() )
            }
        }
    }
}

#[pymodule]
fn inotify_lookup(_py:Python, m:&PyModule) -> PyResult<()> {
    m.add_function( wrap_pyfunction!(register, m)? )?;
    m.add_function( wrap_pyfunction!(unregister, m)? )?;
    m.add_function( wrap_pyfunction!(dump, m)? )?;
    Ok(())
}

#[test]
fn test() -> Result<(), std::io::Error> {
    //TODO: implement integration test
    Ok(())
}