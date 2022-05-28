use std::os::raw::{c_long, };
use std::{ptr, };
use x11_dl::xlib;
use crate::xatom::XAtom;

pub struct XWrap {
    xlib: xlib::Xlib,
    display: *mut xlib::Display,
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

        Self{ xlib, display, root, atoms }
    }

    fn get_xscreens(&self) -> Vec<xlib::Screen> {
        let mut screens = Vec::new();
        let screen_count = unsafe{
            (self.xlib.XScreenCount)( self.display )
        };

        for screen_num in 0..screen_count {
            let screen = unsafe{
                *(self.xlib.XScreenOfDisplay)( self.display, screen_num )
            };
            screens.push(screen);
        }

        return screens;
    }

    fn get_roots(&self) -> Vec<xlib::Window> {
        self.get_xscreens().into_iter().map(|mut s| unsafe{
            (self.xlib.XRootWindowOfScreen)( &mut s )
        }).collect()
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
}

#[test]
pub fn test() {
    let xw = XWrap::new();

}
