# VDM Capability Development Norm
> For Virtual Domain Manager <=v1.0.0

1. Fork this repo and create your own branch with the capability name to contribute, e.g., `inotify-lookup`;

2. Create the capability folder, and add the `README.md` file filling in the following content:
    ```markdown
    # <Capability_Name_Here>
    **This capability aims at: <short_description_here>**

    > Long descriptions in the following graphs.

    ### References
    > (Optional) The reference material link to this capability;

    -----

    ### Dependency
    > The dependency of this capability

    ### Structure
    > List the major folders/files and explains their functions accordingly;

    ### Build
    > (Optional) Your manual build procedure or scripts here

    ### Test
    > Your test procedure or scripts here.
    ```

3. Put your project in the created subfolder, and use wrapper in `__wrapper__` to decorate your entry functions;
    > Or you can manually decorate your functions: takes *one CString* as input, and *one CString* as return value;

3. Add the `manifest.json` file resembling the following format, and use `sbs` to compile the project;
    ```json
    {
        "name": "",             // (required) capability name, '-'/'_' both allowed
        "type": "",             // (required) rust / python / c / cpp
        "version": "",          // (required) version number, e.g., "1.0.0"
        
        "build": {              // **Build Section**
            "dependency": {},   // (optional) support `cargo/pip/conan`
            "script": [],       // build script executed sequentially
            "output": []        // (required) the files to install:
                                //      1) first one is main entry; 2) use `@` for rename
        },

        "runtime": {            // **Runtime section**
            "dependency": {},   // (optional) support `cargo/pip/conan`
            "status":  ""       // (optional) the command line used to check capability status (echo on `stdout`)
            "enable": [],       // the scripts executed sequentially to ENABLE the capability
            "disable": [],      // the scripts executed sequentially to DISABLE the capability
        },

        "metadata": {}          // (required) the functions signatures, use the JSON type system:
                                //      Null, Bool, Number, String, Array, Object
    }
    ```

4. Test your capability;
    - `pyvdm cm enable/disable/status <capability_name>`
    - access the functions via `pyvdm` local handle:
        ```python3
        import json
        from pyvdm.interface with import CapabilityHandleLocal

        handle = CapabilityHandleLocal('<capability_name>')
        func   = handle.func
        args   = json.dumps(args:dict)
        json.loads( func(args) )
        ```

5. Create the Pull Request on Github for code review.
