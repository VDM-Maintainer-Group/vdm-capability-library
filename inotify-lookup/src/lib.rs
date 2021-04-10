
pub mod inotify_lookup {
    use std::net;

    fn init_socket() -> usize {
        unimplemented!();
    }

    fn fini_socket() -> usize {
        unimplemented!();
    }

    fn send_request() -> usize {
        unimplemented!();
    }

    fn recv_message() -> usize {
        unimplemented!();
    }

    /*-----------------------------------------------------------*/
    // #[no_mangle] //not for non-Rust usage
    pub fn inotify_lookup_register(name: &str) -> usize {
        unimplemented!();
    }

    // #[no_mangle] //not for non-Rust usage
    pub fn inotify_lookup_unregister(name: &str) -> usize {
        unimplemented!();
    }

    // #[no_mangle] //not for non-Rust usage
    pub fn inotify_lookup_dump(name: &str) -> String {
        unimplemented!();
    }

}

#[test]
fn test() -> Result<(), std::io::Error> {
    unimplemented!();
}