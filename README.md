cFBuild
==============
**cloudFPGA Build Framework**


Requirements
-------------

### Python Virtualenv
```bash
$ which python3.6
/usr/bin/python3.6
$ virtualenv -p /usr/bin/python3.6 cfenv
$ source cfenv/bin/activate
$ pip install -r requirements.txt
```

Usage
-----------

### Create new cloudFPGA project (cFp)

To create a new cFp, use the `cFBuild` command:
```bash
$ ./cFBuild -h
cloudFPGA Build Framework
cfBuild creates or updates cloudFPGA projects (cFp) based on the cloudFPGA Development Kit (cFDK).

Usage: 
    cfBuild new (--cfdk-version=<cfdkv> | --cfdk-zip=<path-to-zip>)  [--git-url=<git-url>] <path-to-project-folder>
    cfBuild update  <path-to-project-folder>
    
    cfBuild -h|--help
    cfBuild -v|--version

Commands:
    new             Creates a new cFp based on the given cFDK
    update          Update the environment setting of an existing cFp

Options:
    -h --help       Show this screen.
    -v --version    Show version.
    
    --cfdk-version=<cfdkv>      Specifies that the cFDK can be accessed via Github and with cFDK-version should be used.
                                'latest' will use the latest available version.
    --git-url=<git-url>         Uses the given URL to clone cFDK instead the default.
    --cfdk-zip=<path-to-zip>    If the cFDK can't be reached via Github, a zip can be used.

Copyright IBM Research, All Rights Reserved.
Contact: {ngl,fab,wei}@zurich.ibm.com
```

**The script will ask for the type of SRA or cF module --> see cFDK documentation.**

1. New cFp with a cFDK-zip

```bash
./cFBuild new --cfdk-zip=./<path>/cFDK-v0.1.zip <path-to-project-folder>
```
The `project-folder` should not exist (yet) or must be empty (or an new git repository).

2. New cFp using Github

```bash
./cFBuild new --cfdk-version=v0.1 <path-to-project-folder>
```
The `project-folder` should not exist (yet) or must be empty (or an new git repository).
If the default Github URL is not accessible, an alternative can be specified with `-git-url`.

3. Update an existing cFp

If it is necessary to regenerate the environment of the cFp (e.g. switch of SRA type or cFDK version,
 **or after a fresh clone of an existing cFp**), run:
```bash
./cFBuild update <path-to-project-folder>
```

Structure of a cFp
--------------

```bash
$ tree <cFp_repo>
    cFDK/ (submodule)
    TOP/
    └──tcl/ (don't touch, is copied from cFDK) 
    └──xdc/ (add debug nets here)
    └──hdl/
       └──top.vhdl
       └── a.s.o. (if custom hdl files for TOP)
    ROLE/
    └── role1 (or not, depends on PR, etc.)
    └── a.s.o.
    dcps/ (contains the dcps and bitfiles)
    xpr/ (vivado project)
    ip/ (contains the IP cores (generated during build))
    Makefile
    env/
    └── setenv.sh (sets the envrionments)
```

### Push new cFp to a git repository

Basically, follow [this steps](https://help.github.com/en/articles/adding-an-existing-project-to-github-using-the-command-line).
In short:
```bash 
$ cd <cFp_repo>
$ git init
$ git add . 
$ git commit -m "First commit"
$ git remote add origin <remote-repository-URL>
$ git push origin master
```

### cFDK as git submodule

It is recommended, to declare the cFDK folder as git submodule to the cFp git repository. 
Therefore, execute the following:
```bash
$ cd <cFp_repo>
$ git submodule add --name cFDK file://./cFDK/
```
*Before commit, you must manually update the path to the remote location*, if desired.

Hence, overwrite the file `<cFp_repo>/.gitmodules` with the following content:

```config
[submodule "cFDK"]
	path = cFDK
	url = git@github.ibm.com:cloudFPGA/cFDK.git
```
also, update `.git/config` accordingly, from:
```bash
[submodule "cFDK"]
        url = file://./cFDK/
```
to
```bash
[submodule "cFDK"]
        url = git@github.ibm.com:cloudFPGA/cFDK.git
```

Or use the alternative `git-url` as mentioned above.


Afterwards, run: 

```bash
$ git submodule init
$ git submodule update
$ git commit
$ git push
```

Further information about git submodules can be found [here](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

Build a cFp
----------------

See the documentation of cFDK.
In short:
```bash
$ source env/setenv.sh  # DON'T FORGETT!
$ make monolithic
# or 
$ make pr
```

Resulting bitfiles are in `./dcps/`.

Known Limitations/Bugs
-----------------------

* Currently, only the non-PR flow (i.e. `monolithic`) is supported. Hence, it is recommended to:
  * create a cFp per Role
  * The `<cFp-repo>/ROLE/` should contain only one Role. 
  * Answer the question *Name of the (first) Role* with **`default`**.
* SRA `MPIv0_x2Mp_x2Mc` is currently broken
