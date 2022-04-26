# VDM Capability Library

This repo is maintained as a fully-decoupled submodule of [Project VDM](https://github.com/VDM-Maintainer-Group/virtual-domain-manager). 
Feel free to *use or contribute* every best practice in this repo.

**About *Simple Build System***

- Have `pyvdm` installed, you can use `sbs` to invoke the build system as alias to `build.py` file in this repo;

- Bare `sbs build` is equal to `sbs build *` instead of `sbs build .`, which applies to all the sub-folders with `manifest.json` file;

- It is suggested to use a temporary folder for a single capability building, e.g., `mkdir build && cd build && sbs build ..`

-----

### Dependency

**Python 3**: `pip3 install halo pyyaml`

### Structure

- [inotify-lookup](./inotify-lookup)
  
  > find out files one application is watching on, with inotify.


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

