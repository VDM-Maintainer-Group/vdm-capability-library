use std::ops::Add;
use std::ops::Sub;

use x11_dl::xlib;

#[derive(Debug, Copy, Clone, PartialEq)]
pub enum WindowState {
    Modal,
    Sticky,
    MaximizedVert,
    MaximizedHorz,
    Shaded,
    SkipTaskbar,
    SkipPager,
    Hidden,
    Fullscreen,
    Above,
    Below,
}

#[derive(Default, Clone, Debug, PartialEq, Copy)]
pub struct Xyhw {
    pub x: i32,
    pub y: i32,
    pub h: i32,
    pub w: i32,
}

impl Add for Xyhw {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Self {
            x: self.x + other.x,
            y: self.y + other.y,
            w: self.w + other.w,
            h: self.h + other.h,
        }
    }
}

impl Sub for Xyhw {
    type Output = Self;
    fn sub(self, other: Self) -> Self {
        Self {
            x: self.x - other.x,
            y: self.y - other.y,
            w: self.w - other.w,
            h: self.h - other.h,
        }
    }
}

impl Xyhw {
    pub fn new(x:i32, y:i32, h:i32, w:i32) -> Self{
        Self{ x, y, h, w }
    }

    pub const fn center(&self) -> (i32, i32) {
        let x = self.x + (self.w / 2);
        let y = self.y + (self.h / 2);
        (x, y)
    }

    pub const fn volume(&self) -> u64 {
        self.h as u64 * self.w as u64
    }

    pub const fn contains_point(&self, x: i32, y: i32) -> bool {
        let max_x = self.x + self.w;
        let max_y = self.y + self.h;
        (self.x <= x && x <= max_x) && (self.y <= y && y <= max_y)
    }

    pub const fn contains_xyhw(&self, other: &Self) -> bool {
        let other_max_x = other.x + other.w;
        let other_max_y = other.y + other.h;
        self.contains_point(other.x, other.y) && self.contains_point(other_max_x, other_max_y)
    }

}

#[derive(Clone, Debug)]
pub struct ScreenStatus {
    pub name: String,
    pub screen: xlib::Screen,
    pub root: xlib::Window,
    pub xyhw: Xyhw,
}

impl ScreenStatus {
    pub fn new(name: String, screen: xlib::Screen, root: xlib::Window, h: i32, w: i32) -> Self {
        let xyhw = Xyhw::new(0, 0, h, w);
        ScreenStatus{ name, screen, root, xyhw }
    }
}

#[derive(Clone, Debug)]
pub struct WindowStatus {
    pub name: String,
    pub pid: u32,
    //
    pub screen: String,
    pub desktop: u32,
    pub state: Vec<WindowState>,
    pub xyhw: Xyhw
}

impl WindowStatus {

}

