mod xatom;
mod xwrap;
mod xmodel;

use xwrap::XWrap;
use xmodel::{Xyhw, WindowStatus};
use serde_wrapper::jsonify;

#[no_mangle]#[jsonify]
pub fn get_number_of_desktops() -> i32 {
    match XWrap::new().get_number_of_desktops() {
        Some(x) => x as i32,
        None    => -1
    }
}

pub fn set_number_of_desktops(num: u32) {
    XWrap::new().set_number_of_desktops(num);
}

#[no_mangle]#[jsonify]
pub fn get_current_desktop() -> i32 {
    match XWrap::new().get_current_desktop() {
        Some(x) => x as i32,
        None    => -1
    }
}

pub fn set_current_desktop(idx: u32) {
    XWrap::new().set_current_desktop(idx);
}

#[no_mangle]#[jsonify]
pub fn get_windows_by_name(name: String) -> Vec<WindowStatus> {
    XWrap::new().get_windows_by_filter(|w_name, _, _| {
        w_name.contains(&name)
    })
}

#[no_mangle]#[jsonify]
pub fn get_windows_by_pid(pid: u32) -> Vec<WindowStatus> {
    XWrap::new().get_windows_by_filter( |_, w_pid, _| w_pid==pid )
}

#[no_mangle]#[jsonify]
pub fn get_windows_by_xid(xid: u64) -> Vec<WindowStatus> {
    XWrap::new().get_windows_by_filter( |_, _, w_xid| w_xid==xid )
}

#[no_mangle]#[jsonify]
pub fn set_window_by_xid(xid: u64, desktop:u32, states: Vec<String>, xyhw: Xyhw) -> u32 {
    let status = WindowStatus {
        xid, desktop, states, xyhw, ..WindowStatus::default()
    };
    XWrap::new().set_window_status(xid, &status);

    0
}

#[test]
fn test() {
    use std::ffi::CString;
    use serde_json;

    let kwargs:String = r#"{}"#.into();
    let kwargs_1 = CString::new( kwargs.clone() ).unwrap().into_raw();
    println!( "Current number of desktops: {}.", unsafe{
        CString::from_raw( get_number_of_desktops(kwargs_1) ).into_string().unwrap()
    } );
    let kwargs_1 = CString::new( kwargs.clone() ).unwrap().into_raw();
    println!( "Current desktop: {}.", unsafe{
        CString::from_raw( get_current_desktop(kwargs_1) ).into_string().unwrap()
    } );

    let kwargs:String = r#"{"name":"Visual Studio Code"}"#.into();
    let kwargs = CString::new(kwargs.clone()).unwrap().into_raw();
    let status_str = unsafe {
        CString::from_raw( get_windows_by_name(kwargs) ).into_string().unwrap()
    };
    println!("{}", status_str);

    let mut status: Vec<WindowStatus> = serde_json::from_str(&status_str).unwrap();
    status[0].xyhw.x += 48;
    status[0].xyhw.y += 27;

    let kwargs = format!("{{
        \"xid\": {},
        \"desktop\": {},
        \"states\": {:?},
        \"xyhw\": {{ \"x\":{},\"y\":{},\"h\":{},\"w\":{} }}
    }}", status[0].xid, status[0].desktop, status[0].states,
         status[0].xyhw.x,status[0].xyhw.y,status[0].xyhw.h,status[0].xyhw.w)
    ;

    let kwargs_1 = CString::new( kwargs.clone() ).unwrap().into_raw();
    let res = unsafe {
        CString::from_raw( set_window_by_xid( kwargs_1 ) ).into_string().unwrap()
    };
    println!("res: {}", res);
}
