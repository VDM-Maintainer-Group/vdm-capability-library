use std::error::Error;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


mod _priv {
    use std::error::Error;
    use neli::{
        consts::{nl::*, socket::*},
        err::NlError,
        nl::{Nlmsghdr, NlPayload},
        socket::NlSocketHandle,
        types::{Buffer,}
    };

    #[allow(dead_code)] //Rust lint open issue, #47133
    const NETLINK_USER: i32 = 31;   // (fixed) netlink specific magic number
    const MAX_NAME_LEN: i32 = 1024; // (fixed) maximum length of app name
    const PATH_MAX    : i32 = 4096; // (fixed) maximum length of inode pathname
    const MAX_DUMP_LEN: i32 = 1000; // maximum number of received dump
    /* struct __attribute__((__packed__)) req_msg_t {
        int op;
        char comm_name[MAX_NAME_LEN];
    }; */
    enum Command {
        InotifyReqAdd = 0x01,
        InotifyReqRm  = 0x02,
        InotifyReqDump= 0x04,
    }

    fn init_socket() -> Result<(), Box<dyn Error>> {
        let mut socket = NlSocketHandle::connect(
            NlFamily::UnrecognizedVariant(NETLINK_USER), None, &[0]);
        
        unimplemented!();
    }

    fn fini_socket() -> Result<(), Box<dyn Error>> {
        unimplemented!();
    }

    fn send_request() {
        unimplemented!();
    }

    fn recv_message() {
        unimplemented!();
    }
}

#[pyfunction]
pub fn inotify_lookup_register(name: &str) -> PyResult<usize> {
    unimplemented!();
}

#[pyfunction]
pub fn inotify_lookup_unregister(name: &str) -> PyResult<usize> {
    unimplemented!();
}

#[pyfunction]
pub fn inotify_lookup_dump(name: &str) -> PyResult<String> {
    unimplemented!();
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