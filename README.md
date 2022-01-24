# VDM Capability Library

This repo is maintained as a fully-decoupled submodule of [Project VDM](https://github.com/VDM-Maintainer-Group/virtual-domain-manager). 
Feel free to *use or contribute* every best practice in this repo.

-----

### Dependency

**Python 3**: `halo`, `pyyaml`

### Structure

- [ ] [browser-helper](./browser-helper)

  > dump/restore the browsing tabs in the web browser.

- [x] [inotify-lookup](./inotify-lookup)

  > find out files one application is watching on, with inotify.

- [ ] [note-film](./note-fild)

  > allow to take notes on any application, any where, any time~

- [ ] [system-tweaker](./system-tweaker)

  > bridge the gap among different Linux desktops or distributions, with a collection of system-related configuration utilities.

- [ ] [window-helper](./window-helper)

  > easy manipulate windows and workspace under different DE compatible with freedesktop

### Build

- With *Simple Build System*:

  ```bash
  ./build.py build
  ```

- Manually build:

  ```bash
  mkdir build; cd build; cmake ..; make
  ```

### Test

```bash
./build.py test
```




### How to contribute

Please refer to the tutorial [here](CONTRIBUTING.md).

### About *Simple Build System*

- Have `pyvdm` installed, you can use `sbs` to invoke the build system;

- `sbs build` is equal to `sbs build *`, trying to find `manifest.json` in all the sub-folders.

- The suggested usage for single capability testing:

  ```bash
  mkdir build; cd build;
  sbs build ..
  sbs install ..
  ```

