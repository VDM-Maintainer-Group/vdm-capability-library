use std::os::raw::{c_int, c_uint, c_long, c_ulong, };
use std::{ptr, };
use std::ffi::CStr;
use x11_dl::xlib;
use crate::xatom::XAtom;
use crate::xmodel::{ScreenStatus, };

pub struct XWrap {
    xlib: xlib::Xlib,
    display: *mut xlib::Display,
    screens: Vec<ScreenStatus>,
    root: xlib::Window,
    atoms: XAtom
}

#[allow(dead_code)]
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
        self.sync();
    }

    pub fn sync(&self) {
        unsafe{
            (self.xlib.XSync)(self.display, xlib::False);
        }
    }

    fn set_desktop_prop(&self, atom: c_ulong, data: &[u32]) {
        let mut msg: xlib::XClientMessageEvent = unsafe { std::mem::zeroed() };

        msg.type_ = xlib::ClientMessage;
        msg.format = 32;
        msg.send_event = 1;
        // msg.display = self.display;
        msg.window  = self.root;
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
    pub fn set_number_of_desktops(&self, num: u32) {
        self.set_desktop_prop(self.atoms.NetNumberOfDesktops, &[num])
    }

    pub fn set_current_desktop(&self, idx: u32) {
        self.set_desktop_prop(self.atoms.NetCurrentDesktop, &[idx, xlib::CurrentTime as u32])
    }
}

impl XWrap {
    pub fn get_window_geometry(&self, window: xlib::Window) {

    }
}
