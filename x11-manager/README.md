# X11 Manager
**This capability aims at: provide X11 window and desktop control via EWMH and ICCCM.**



### References
1. [Extended Window Manager Hints - freedesktop.org](https://specifications.freedesktop.org/wm-spec/wm-spec-1.3.html)
2. [pyewmh - github.com](https://github.com/parkouss/pyewmh)
3. [leftwm - github.com](https://github.com/leftwm/leftwm)

-----

### Dependency
- `libxcb-util-dev`

### Structure
> TBD.

### TODO
- [x] get/set number of desktops
- [x] get/set current focused desktop

- [x] get window props by "substring match":
    - if multiple windows match, return all as a list;
    - return `geometry`, `window state` and `desktop index`, e.g., `wmctrl -lG`;
    - together return with current screen geometry;
      (if screens disconnected, shrink to the northwest corner)
- [x] get window props by "window xid" or "_NET_WM_PID"
- [x] set window props by "window xid"
