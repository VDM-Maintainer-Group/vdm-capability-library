# Inotify Lookup

**This capability aims at: find out files one application is watching on, with inotify.**

The efficient solution exists in `inotify_group` reverse lookup, however, there is no existing mechanism available. So, I hook both the `inotify_add_watch` and `inotify_rm_watch` to maintain the existing watcher list for each process.

Netlink will response to request of `comm_name` from users pace in unicast (no encryption/authentication considered for now).

Here lists some applications using `inotify`:

- **Editors**: `code`, `Typora`, `okular`, etc.

### References

1. https://security.stackexchange.com/questions/210897/why-is-there-a-need-to-modify-system-call-tables-in-linux
2. https://stackoverflow.com/questions/2103315/linux-kernel-system-call-hooking-example
3. https://stackoverflow.com/questions/11915728/getting-user-process-pid-when-writing-linux-kernel-module
4. https://uwnthesis.wordpress.com/2016/12/26/basics-of-making-a-rootkit-from-syscall-to-hook/
5. https://stackoverflow.com/questions/58819136/is-it-possible-to-dump-inode-information-from-the-inotify-subsystem

-----

### Dependency

`cargo`, `cmake>=3.0.0`, `linux-headers-*`

### Structure

- `inotify-hook` (kernel hook module)
- `inotify-lookup` (user-space netlink client)
- `inotify-lookup-py` (user-space netlink client, for debug purpose)

### Build

- With *Simple Build System*:

  ```bash
  ./build.py build inotify-lookup
  ```

- Manually build:

  ```bash
  # for netlink client
  cargo build --release
  
  # for kernel hook module build
  mkdir -p build; cd build; cmake ..; make
  ```

### Test

```bash
# firstly insert the kernel module
sudo insmod build/inotify-hook/inotify_hook.ko
# `run_test` in `inotify-lookup/src/lib.rs`
cargo test
# remove the kernel module after test
sudo rmmod inotify_hook
```



### Todo

- Add DKMS compiling
