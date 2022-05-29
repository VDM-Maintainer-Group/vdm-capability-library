mod xatom;
mod xwrap;
mod xmodel;

use xwrap::XWrap;
use xmodel::WindowStatus;
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

// #[no_mangle]#[jsonify]
pub fn get_window_by_name(name: String) -> Vec<WindowStatus> {
    XWrap::new().get_windows_by_filter(|w_name, _, _| {
        w_name.contains(&name)
    })
}

// #[no_mangle]#[jsonify]
pub fn get_window_by_pid(pid: u32) -> Vec<WindowStatus> {
    XWrap::new().get_windows_by_filter( |_, w_pid, _| w_pid==pid )
}

// #[no_mangle]#[jsonify]
pub fn get_window_by_wid(wid: u64) -> Vec<WindowStatus> {
    XWrap::new().get_windows_by_filter( |_, _, w_wid| w_wid==wid )
}

#[test]
fn test() {
    let xw = XWrap::new();

    xw.set_number_of_desktops(2);
    xw.set_current_desktop(1);
    xw.sync();
}
