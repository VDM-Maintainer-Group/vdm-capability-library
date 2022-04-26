# VDM Capability Development Norm
> For Virtual Domain Manager <=v1.0.0

1. Fork this repo and create your own branch with the capability name to contribute, e.g., `inotify-lookup`.

2. Create the capability subfolder, and add the `README.md` file with the following content:
    ```markdown
    # <Capability_Name_Here>
    **This capability aims at: <short_description_here>**

    > Long descriptions in the following graphs.

    ### References
    > (Optional) The reference material link to this capability.

    -----

    ### Dependency
    > The dependency of this capability.

    ### Structure
    > List the major folders/files and explains their functions accordingly.

    ### Build
    > (Optional) Your manual build procedure or scripts here.

    ### Test
    > (Optional) Your test procedure or scripts here.
    ```

3. Put your project in the created subfolder, and use wrapper (in the `__wrapper__` folder) to decorate your entry functions.
    > Or you can manually decorate your functions: take *one json-format CString* as input argument, and *one json-format CString* as return value;

3. Add the `manifest.json` file resembling the following format, and use `sbs build .` to compile the project.
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

4. Test your capability:
    - install your capability with sbs: `sbs install .`
    - status control via pyvdm: `pyvdm cm <enable/disable/status> <capability_name>`
    - access the functions via pyvdm local handle:
        ```python3
        import json
        from pyvdm.interface.CapabilityLibrary import CapabilityHandleLocal

        handle = CapabilityHandleLocal('<capability_name>')
        func   = handle.func
        args   = json.dumps(args:dict)
        json.loads( func(args) )
        ```

5. Create the Pull Request on this Github repo for code review.
