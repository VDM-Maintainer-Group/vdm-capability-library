extern crate proc_macro;

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, parse_quote};

#[proc_macro_attribute]
pub fn jsonify(_attr: TokenStream, input: TokenStream) -> TokenStream {
    let func = parse_macro_input!(input as syn::ItemFn);
    let mut block = func.block;
    let mut sig = func.sig.clone();

    sig.inputs.iter_mut().for_each(|arg|{
        match arg {
            syn::FnArg::Typed(pat) => {
                let (_pat, _ty) = ( pat.pat.clone(), pat.ty.clone() );
                // change function input type to "String"
                pat.ty = syn::parse( quote!(String).into() ).unwrap();
                // build deserialize statements
                let _stmt: syn::Stmt = parse_quote!(
                    let #_pat:#_ty = match serde_json::from_str(&#_pat) {
                        Ok(res) => res,
                        Err(_) => return "".into() //panic and exit
                    };
                ); 
                block.stmts.insert(0, _stmt);
            },
            _ => {}
        }
    });
    // change function output type to "String"
    sig.output = syn::parse( quote!(->String).into() ).unwrap();

    // generate output
    quote!(
        pub #sig {
            let res = { #block };
            serde_json::to_string(&res).unwrap_or( "".into() )
        }
    ).into()
}
