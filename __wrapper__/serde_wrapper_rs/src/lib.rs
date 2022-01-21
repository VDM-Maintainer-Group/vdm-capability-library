extern crate proc_macro;

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, parse_quote};

#[proc_macro_attribute]
pub fn jsonify(_attr: TokenStream, input: TokenStream) -> TokenStream {
    let func = parse_macro_input!(input as syn::ItemFn);
    let mut block = func.block.clone();
    let mut sig = func.sig.clone();

    // build deserialize statements
    sig.inputs.iter().for_each(|arg|{
        match arg {
            syn::FnArg::Typed(pat) => {
                let (_pat, _ty) = ( pat.pat.clone(), pat.ty.clone() );
                let _pat_name:String = quote!(#_pat).to_string();

                let _stmt: syn::Stmt = parse_quote!(
                    let #_pat:#_ty = match serde_json::from_value( kwargs[#_pat_name].clone() ) {
                        Ok(value) => value,
                        Err(_) => return "".into()
                    };
                );

                block.stmts.insert(0, _stmt);
            },
            _ => {}
        }
    });

    //change function input to monolithic String
    sig.inputs = parse_quote!(kwargs:String);
    // change function output type to "String"
    sig.output = parse_quote!(->String);

    // build wrapped block of statements
    let block: syn::Block = syn::parse(
        quote!({
            let kwargs:serde_json::Value = serde_json::from_str(&kwargs).unwrap(); //panic
            let res = { #block };
            serde_json::to_string(&res).unwrap_or( "".into() )
        }).into()
    ).unwrap();
    let block = Box::new(block);

    // generate output
    let wrapped_func = syn::ItemFn {
        attrs: func.attrs.clone(),
        vis: syn::parse( quote!(pub).into() ).unwrap(),
        sig, block
    };
    // println!("{}", quote!( #wrapped_func ));
    quote!( #wrapped_func ).into()
}
