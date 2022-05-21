use std::{ptr, slice};
use x11_dl::xlib;

pub struct XWrap {
    xlib: xlib::Xlib,
    display: *mut xlib::Display,
    root: xlib::Window
}

impl XWrap {
    pub fn new() -> Self {
        let xlib = xlib::Xlib::open()expect("Couldn't not connect to Xorg Server");
        let display = unsafe{
            (xlib.XOpenDisplay)( ptr::null() )
        };

        assert!(!display.is_null(), "Null pointer in display");

        let root = unsafe {
            (xlib.XDefaultRootWindow)(display)
        };

        Self{ xlib, display, root }
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
            (self.xlib.XRootWindowsOfScreen( &mut s ))
        }).collect()
    }
    
}

pub fn test() {
    let xw = XWrap();

    // get screen
    let mut screens = Vec::new();
    let screen_count = unsafe{
        (xlib.XScreenCount)()
    }
}
