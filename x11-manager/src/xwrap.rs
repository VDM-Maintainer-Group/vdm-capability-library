use std::os::raw::{c_long, c_ulong, c_int, c_uint, c_char, c_uchar, };
use std::{ptr, slice};
use std::ffi::{CString, };
use x11_dl::xlib;
use crate::xatom::XAtom;
use crate::xmodel::{Xyhw, ScreenStatus, WindowStatus};

const MAX_PROPERTY_VALUE_LEN: c_long = 4096;

pub struct XWrap {
    xlib: xlib::Xlib,
    display: *mut xlib::Display,
    screens: Vec<ScreenStatus>,
    root: xlib::Window,
    atoms: XAtom
}

impl XWrap {
    pub fn new() -> Self {
        let xlib = xlib::Xlib::open().expect("Couldn't not connect to Xorg Server");
        let display = unsafe{
            (xlib.XOpenDisplay)( ptr::null() )
        };
        assert!(!display.is_null(), "Null pointer in display");

        let atoms = XAtom::new(&xlib, display);
        let root = unsafe {
            (xlib.XDefaultRootWindow)(display)
        };

        let mut screens = Vec::new();
        let screen_count = unsafe{
            (xlib.XScreenCount)( display )
        };
        for screen_num in 0..screen_count {
            let (name, screen, root, h, w) = unsafe{
                // let _name = (xlib.XDisplayString)()
                let mut _screen = *(xlib.XScreenOfDisplay)( display, screen_num );
                let _root   = (xlib.XRootWindowOfScreen)( &mut _screen );
                let _height = (xlib.XHeightOfScreen)( &mut _screen );
                let _width  = (xlib.XWidthOfScreen)( &mut _screen );
                let _name = format!("{}x{}-{}", _width, _height, screen_num);
                (_name, _screen, _root, _height, _width)
            };
            screens.push( ScreenStatus::new(name, screen, root, h, w) );
        }

        Self{ xlib, display, screens, root, atoms }
    }
    
    fn send_event(&self, event: &mut xlib::XEvent, window:Option<xlib::Window>, mask: Option<c_long>) {
        let window = window.unwrap_or( self.root );
        let mask = mask.unwrap_or( xlib::SubstructureRedirectMask | xlib::SubstructureNotifyMask );
        let propagate: i32 = 0;

        unsafe{
            (self.xlib.XSendEvent)(self.display, window, propagate, mask, event);
        }
        self.flush();
    }

    fn flush(&self) {
        unsafe { (self.xlib.XFlush)(self.display) };
    }

    pub fn sync(&self) {
        unsafe{
            (self.xlib.XSync)(self.display, xlib::False);
        }
    }

    fn get_property(&self, window: xlib::Window, property: xlib::Atom, r#type: xlib::Atom) -> Option<(c_ulong, *const c_uchar)> {
        let mut format_return: i32 = 0;
        let mut nitems_return: c_ulong = 0;
        let mut type_return: xlib::Atom = 0;
        let mut bytes_after_return: xlib::Atom = 0;
        let mut prop_return: *mut c_uchar = unsafe { std::mem::zeroed() };
        unsafe {
            let status = (self.xlib.XGetWindowProperty)(
                self.display, window, property, 0, MAX_PROPERTY_VALUE_LEN / 4, xlib::False, r#type,
                &mut type_return, &mut format_return, &mut nitems_return, &mut bytes_after_return, &mut prop_return
            );
            if status==i32::from(xlib::Success) && !prop_return.is_null() {
                return Some( (nitems_return, prop_return) );
            }
        }
        None
    }

    fn get_text_prop(&self, window: xlib::Window, atom: xlib::Atom) -> Option<String> {
        unsafe {
            let mut text_prop: xlib::XTextProperty = std::mem::zeroed();
            let status: c_int =
                (self.xlib.XGetTextProperty)(self.display, window, &mut text_prop, atom);
            if status == 0 {
                return None;
            }
            if let Ok(s) = CString::from_raw(text_prop.value.cast::<c_char>()).into_string() {
                return Some(s);
            }
        };
        None
    }

    fn get_window_prop(&self, window: xlib::Window, property: xlib::Atom) -> Option<u32> {
        let (_, prop_return) = self.get_property(window, property, xlib::XA_CARDINAL)?;
        unsafe {
            #[allow(clippy::cast_lossless, clippy::cast_ptr_alignment)]
            let prop = *prop_return.cast::<u32>();
            Some(prop)
        }
    }

    fn set_window_prop(&self,  window: xlib::Window, atom: c_ulong, data: &[u32]) {
        let mut msg: xlib::XClientMessageEvent = unsafe { std::mem::zeroed() };

        msg.type_ = xlib::ClientMessage;
        msg.format = 32;
        msg.send_event = 1;
        // msg.display = self.display;
        msg.window  = window;
        msg.message_type = atom;

        for (i,x) in data.iter().enumerate() {
            msg.data.set_long(i, *x as c_long);
        }

        let mut ev: xlib::XEvent = msg.into();
        self.send_event( &mut ev, None, None );
    }
}

// EWMH spec, https://specifications.freedesktop.org/wm-spec/wm-spec-1.3.html
impl XWrap {
    pub fn get_number_of_desktops(&self) -> Option<u32> {
        self.get_window_prop(self.root, self.atoms.NetNumberOfDesktops)
    }

    pub fn set_number_of_desktops(&self, num: u32) {
        self.set_window_prop(self.root, self.atoms.NetNumberOfDesktops, &[num]);
    }

    pub fn get_current_desktop(&self) -> Option<u32> {
        self.get_window_prop(self.root, self.atoms.NetCurrentDesktop)
    }

    pub fn set_current_desktop(&self, idx: u32) {
        self.set_window_prop(self.root, self.atoms.NetCurrentDesktop, &[idx, xlib::CurrentTime as u32]);
        self.sync();
    }

    pub fn get_window_desktop(&self, window: xlib::Window) -> Option<u32> {
        self.get_window_prop(window, self.atoms.NetWMDesktop)
    }

    pub fn set_window_desktop(&self, window: xlib::Window, idx: u32) {
        self.set_window_prop(window, self.atoms.NetWMDesktop, &[idx, 1]);
    }

    pub fn get_window_name(&self, window: xlib::Window) -> Option<String> {
        if let Some(text) = self.get_text_prop(window, self.atoms.NetWMName) {
            return Some(text);
        }
        if let Some(text) = self.get_text_prop(window, xlib::XA_WM_NAME) {
            return Some(text);
        }
        None
    }

    pub fn get_window_pid(&self, window: xlib::Window) -> Option<u32> {
        self.get_window_prop(window, self.atoms.NetWMPid)
    }

    pub fn get_window_states_atoms(&self, window: xlib::Window) -> Vec<xlib::Atom> {
        if let Some( (nitems_return, prop_return) ) = self.get_property(window, self.atoms.NetWMState, xlib::XA_ATOM) {
            unsafe {
                #[allow(clippy::cast_lossless, clippy::cast_ptr_alignment)]
                let ptr = prop_return as *const c_ulong;
                let results: &[xlib::Atom] = slice::from_raw_parts(ptr, nitems_return as usize);
                results.to_vec()
            }
        }
        else {
            vec![]
        }
    }

    pub fn get_window_states(&self, window: xlib::Window) -> Vec<String> {
        self.get_window_states_atoms(window).iter().map( |a| self.atoms.get_name(*a).into() ).collect()
    }

    pub fn set_window_states(&self, window: xlib::Window, states:&[&str]) {
        let mut maximum_state = -2;

        for state in states.iter() {
            match state {
                &"NetWMStateMaximizedVert" | &"NetWMStateMaximizedHorz" => {
                    maximum_state += 1;
                }
                &"NetWMStateHidden" => {
                    self.set_window_prop(window, self.atoms.NetWMState, &[1, self.atoms.NetWMStateHidden as u32, 0, 1]);
                }
                &"NetWMStateShaded" => {
                    self.set_window_prop(window, self.atoms.NetWMState, &[1, self.atoms.NetWMStateShaded as u32, 0, 1]);
                }
                &"NetWMStateFullscreen" => {
                    self.set_window_prop(window, self.atoms.NetWMState, &[1, self.atoms.NetWMStateFullscreen as u32, 0, 1]);
                }
                &"NetWMStateAbove" => {
                    self.set_window_prop(window, self.atoms.NetWMState, &[1, self.atoms.NetWMStateAbove as u32, 0, 1]);
                }
                &"NetWMStateBelow" => {
                    self.set_window_prop(window, self.atoms.NetWMState, &[1, self.atoms.NetWMStateBelow as u32, 0, 1]);
                }
                _ => {}
            };
        }
        
        if maximum_state >= 0{
            self.set_window_prop(window, self.atoms.NetWMState,
                &[1, self.atoms.NetWMStateMaximizedVert as u32, self.atoms.NetWMStateMaximizedHorz as u32, 1]);
        }
    }
}

impl XWrap {
    pub fn get_window_geometry(&self, window: xlib::Window) -> Option<Xyhw> {
        let mut root_return: xlib::Window = 0;
        let mut x_return: c_int = 0;
        let mut y_return: c_int = 0;
        let mut width_return: c_uint = 0;
        let mut height_return: c_uint = 0;
        let mut border_width_return: c_uint = 0;
        let mut depth_return: c_uint = 0;

        unsafe {
            let status = (self.xlib.XGetGeometry)(
                self.display, window,
                &mut root_return, &mut x_return, &mut y_return, &mut width_return, &mut height_return,
                &mut border_width_return, &mut depth_return
            );

            if status == 0 {
                return None
            }
        }
        Some(Xyhw {
            x: x_return,
            y: y_return,
            w: width_return as i32,
            h: height_return as i32,
        })
    }

    pub fn set_window_geometry(&self, window: xlib::Window, xyhw: Xyhw) {
        let mut gravity_flag: u32 = 0x0800;
        if xyhw.x != 0 { gravity_flag |= 0x0400; }
        if xyhw.y != 0 { gravity_flag |= 0x0200; }
        if xyhw.w != 0 { gravity_flag |= 0x0100; }
        if xyhw.h != 0 { gravity_flag |= 0x0080; }
        self.set_window_prop(window, self.atoms.NetMoveResizeWindow,
            &[gravity_flag, xyhw.x as u32, xyhw.y as u32, xyhw.w as u32, xyhw.h as u32]);
    }

    pub fn get_window_status(&self, screen: Option<&ScreenStatus>, window: xlib::Window) -> WindowStatus {
        // name: String, pid: u32, screen: String, desktop: u32, state: String, xyhw: Xyhw
        let name    = self.get_window_name(window).unwrap_or( "".into() );
        let pid     = self.get_window_pid(window).unwrap_or(0);
        let screen  = screen.and_then( |x| Some(x.name.to_owned()) ).unwrap_or( "".into() );
        let desktop = self.get_window_desktop(window).unwrap_or(0);
        let states  = self.get_window_states(window);
        let xyhw    = self.get_window_geometry(window).unwrap_or_default();

        WindowStatus{ xid:window, name, pid, screen, desktop, states, xyhw }
    }

    pub fn set_window_status(&self, window: xlib::Window, status: &WindowStatus) {
        self.set_window_desktop(window, status.desktop);
        self.set_window_states(window, 
            & status.states.iter().map(std::ops::Deref::deref).collect::<Vec<&str>>()
        );
        self.set_window_geometry(window, status.xyhw);
        self.sync();
    }

    pub fn get_windows_by_filter<F>(&self, filter: F) -> Vec<WindowStatus>
    where F: Fn(String, u32, u64) -> bool
    {
        let mut results = Vec::new();

        for s in self.screens.iter() {
            let (status, windows) = unsafe {
                let mut root_return: xlib::Window = std::mem::zeroed();
                let mut parent_return: xlib::Window = std::mem::zeroed();
                let mut array: *mut xlib::Window = std::mem::zeroed();
                let mut length: c_uint = std::mem::zeroed();
                let status: xlib::Status = (self.xlib.XQueryTree)(
                    self.display, s.root,
                    &mut root_return, &mut parent_return, &mut array, &mut length
                );
                let windows: &[xlib::Window] = slice::from_raw_parts(array, length as usize);

                (status, windows)
            };

            match status {
                1 /* XcmsSuccess */ | 2 /* XcmsSuccessWithCompression */ => {
                    results.extend(
                        windows.iter().filter_map(|w| {
                            let name = self.get_window_name( w.to_owned() ).unwrap_or_default();
                            let pid  = self.get_window_pid( w.to_owned() ).unwrap_or_default();
                            let wid  = w.to_owned();
                            match filter(name, pid, wid) {
                                true => Some( self.get_window_status(Some(s), *w) ),
                                false => None
                            }
                        })
                    )
                }
                0 /* XcmsFailure */ | _ /* Unknown status*/ => {}
            };
        }

        results
    }
}
