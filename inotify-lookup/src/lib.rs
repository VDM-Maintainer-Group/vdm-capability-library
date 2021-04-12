use std::error::Error;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


mod _priv {
    use std::error::Error;

    fn init_socket() -> Result<(), Box<dyn Error>> {
        unimplemented!();
    }

    fn fini_socket() -> Result<(), Box<dyn Error>> {
        unimplemented!();
    }

    fn send_request() {
        unimplemented!();
    }

    fn recv_message() {
        unimplemented!();
    }
}

#[pyfunction]
pub fn inotify_lookup_register(name: &str) -> PyResult<usize> {
    unimplemented!();
}

#[pyfunction]
pub fn inotify_lookup_unregister(name: &str) -> PyResult<usize> {
    unimplemented!();
}

#[pyfunction]
pub fn inotify_lookup_dump(name: &str) -> PyResult<String> {
    unimplemented!();
}

#[pymodule]
fn inotify_lookup(_py:Python, m:&PyModule) -> PyResult<()> {
    m.add_function( wrap_pyfunction!(inotify_lookup_register, m)? )?;
    m.add_function( wrap_pyfunction!(inotify_lookup_unregister, m)? )?;
    m.add_function( wrap_pyfunction!(inotify_lookup_dump, m)? )?;
    Ok(())
}

#[test]
fn test() -> Result<(), std::io::Error> {
    unimplemented!();
}