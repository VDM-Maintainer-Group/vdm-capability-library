mod xatom;
mod xwrap;

use xwrap::XWrap;
// #[no_mangle]#[jsonify]

#[test]
fn test() {
    let xw = XWrap::new();

    xw.set_number_of_desktops(2);
    xw.set_current_desktop(1);
    xw.sync();
}
