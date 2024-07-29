# VDM Capability Library

This repo is maintained as a fully-decoupled submodule of [Project VDM](https://github.com/VDM-Maintainer-Group/virtual-domain-manager). 
Feel free to *use or contribute* every best practice in this repo.

**About *Simple Build System***

- Have `pyvdm` installed, you can use `sbs` to invoke the build system as alias to `build.py` file in this repo;

- Bare `sbs build` is equal to `sbs build *` instead of `sbs build .`, which applies to all the sub-folders with valid `manifest.json` file;

-----

### Dependency

**Python 3**: `halo`, `pyyaml`

### Structure

- libfrida
  > TODO: provide safe (limited) binding for [frida](https://github.com/frida/frida) for dynamic instrumentation.

- [inotify-lookup](./inotify-lookup)
  
  > find out files one application is watching on, with inotify.

- [x11-manager](./x11-manager)

  > provide X11 window and desktop control via `libxcb`.

- [browser-bridge](./browser-bridge)

  > It provides your browser with VDM-Compatibility together with a connector program.

### Build

```bash
./build.py build
```

### Install

```bash
./build.py install
```

### Test

```bash
./build.py test
```

### How to contribute

Please refer to the tutorial [here](CONTRIBUTING.md).

