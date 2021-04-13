use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[repr(u8)]
pub enum InotifyOp {
    InotifyReqAdd = 0x01,
    InotifyReqRm  = 0x02,
    InotifyReqDump= 0x04,
}
const MAX_DUMP_LEN: usize = 1000; // maximum number of received dump

mod _priv {
    use super::InotifyOp;
    use std::process::id as getpid;
    use neli::{
        consts::{nl::*, socket::*},
        err::NlError,
        nl::{Nlmsghdr, NlPayload},
        socket::NlSocketHandle,
        types::{Buffer,}
    };

    #[allow(dead_code)] //Rust lint open issue, #47133
    const NETLINK_USER: i32 = 31;   // (fixed) netlink specific magic number
    const MAX_NAME_LEN: usize = 1024; // (fixed) maximum length of app name
    const MAX_PATH_LEN: usize = 4096; // (fixed) maximum length of inode pathname
    struct ReqMessage {
        op : libc::c_int,
        comm_name: [char; MAX_NAME_LEN]
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
            NlFamily::UnrecognizedVariant(NETLINK_USER), Some(getpid()), &[0])?;
        Ok(socket)
    }

    pub fn send_request(socket:&mut NlSocketHandle, op:InotifyOp, name:&str) -> Result<(),NlError> {
        let mut message = ReqMessage{
            op : op as libc::c_int,
            comm_name : [0 as char; MAX_NAME_LEN]
        };
        for (i, x) in name.chars().enumerate() {
            message.comm_name[i] = x;
        }
        let _message = unsafe{ any_as_u8_slice(&message) };
        
        let nlhdr = {
            let len = None;
            let nl_type = 0 as u16;
            let flags = NlmFFlags::new(&[]);
            let seq = None;
            let pid = None;
            let payload = NlPayload::Payload(_message);
            Nlmsghdr::new(len, nl_type, flags, seq, pid, payload)
        };
        socket.send(nlhdr)?;

        Ok(())
    }

    pub fn recv_message(socket:NlSocketHandle) {
        unimplemented!();
    }
}

fn inotify_send_request(op:InotifyOp, name:&str) -> Result<(), ()> {
    if let Ok(mut socket) = _priv::get_socket() {
        match _priv::send_request(&mut socket, op, name) {
            Ok(_) => Ok(()),
            Err(_) => Err(())
        }
    }
    else {
        Err(())
    }
}

#[pyfunction]
pub fn inotify_lookup_register(name: &str) -> PyResult<isize> {
    match inotify_send_request(InotifyOp::InotifyReqAdd, name) {
        Ok(_) => Ok(0),
        Err(_) => Ok(-1)
    }
}

#[pyfunction]
pub fn inotify_lookup_unregister(name: &str) -> PyResult<isize> {
    match inotify_send_request(InotifyOp::InotifyReqRm, name) {
        Ok(_) => Ok(0),
        Err(_) => Ok(-1)
    }
}

#[pyfunction]
pub fn inotify_lookup_dump(name: &str) -> PyResult<Vec<String>> {
    if let Err(_) = inotify_send_request(InotifyOp::InotifyReqDump, name) {
        return Ok(Vec::<String>::new());
    }
    
    let mut result = Vec::<String>::with_capacity(MAX_DUMP_LEN);
    //TODO: receive message
    Ok(result)
}

#[pymodule]
fn inotify_lookup(_py:Python, m:&PyModule) -> PyResult<()> {
    m.add_function( wrap_pyfunction!(inotify_lookup_register, m)? )?;
    m.add_function( wrap_pyfunction!(inotify_lookup_unregister, m)? )?;
    m.add_function( wrap_pyfunction!(inotify_lookup_dump, m)? )?;
    Ok(())
}

#[test]
fn test() -> Result<(), std::io::Error> {
    unimplemented!();
}