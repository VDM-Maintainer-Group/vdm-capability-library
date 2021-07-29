extern crate serde_json;
extern crate proc_macro;

use proc_macro::TokenStream;
use quote::quote;
use syn::parse_macro_input;

#[proc_macro]
pub fn jsonify(input: TokenStream) -> TokenStream {
    let func = parse_macro_input!(input as syn::ItemFn);
    let sig = func.sig.clone();

    // cloned sig change to: inputs with "&String", output with "&String"

    // build deserialize statements
    let args_ser = quote!();

    // generate output
    quote!(
        pub fn #sig {
            #args_ser
            let res = { #func.block };
            // return serialized output
            serde_json::to_string(res).unwrap_or("".into())
        }
    ).into()
}
