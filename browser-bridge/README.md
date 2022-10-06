# Browser Bridge
**This capability aims at: dump and restore the browsing tabs in the common web browsers.**



### References
1. [chrome-gnome-shell](https://gitlab.gnome.org/GNOME/chrome-gnome-shell)

-----

### Dependency
- `npm`, `nodejs`, `python3-pip`

### Structure
- `connector` (connector program and manifest file)
- `extension` (source code for browser extension)
- `scripts` (used for install connector/extension)

### Development
```bash
sbs dev
```

### Build
```bash
sbs build
```

### Install
```bash
sbs install
```

### Test
N/A.

### Todo
- [ ] install extensions via install scripts;
