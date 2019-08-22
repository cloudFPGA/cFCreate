cFBuild
==============
**cloudFPGA Build Framework**


Requirements
-------------
The cFBuild script has some python dependencies, hence we recommend the usage of virtualenvs. 

**This python Virtual environment is only required for the execution of cFBuild, not for the build of the FPGA bistreams in a cFp!**

### Setup your Virtualenv

(we recommend the use of python3.5 or python3.6)

If you received this repository as Zip-folder, extract it into `<your-path>/cFBuild`. Otherwise clone this repositroy into `<your-path/cFBuild`. 

```bash
$ cd <your-path>/cFBuid/
$ which python3.6
/usr/bin/python3.6
$ virtualenv -p /usr/bin/python3.6 cfenv
$ source cfenv/bin/activate
$ pip install -r requirements.txt
```

You may have to install `pip` and `virtualenv` first: 
```bash
$ sudo su
$ /usr/bin/python3.6 -m ensurepip
$ pip3 install virtualenv
$ exit
```

Usage
-----------
```bash
$ ./cFBuild -h
cloudFPGA Build Framework
cFBuild creates or updates cloudFPGA projects (cFp) based on the cloudFPGA Development Kit (cFDK).

Usage: 
    cFBuild new (--cfdk-version=<cfdkv> | --cfdk-zip=<path-to-zip>)  [--git-url=<git-url>] [--git-init] <path-to-project-folder>
    cFBuild update  <path-to-project-folder>
    cFBuild adorn (--cfa-repo=<cfagit> | --cfa-zip=<path-to-zip>) <folder-name-for-addon> <path-to-project-folder>
    
    cFBuild -h|--help
    cFBuild -v|--version

Commands:
    new             Creates a new cFp based on the given cFDK
    update          Update the environment setting of an existing cFp
    adorn           Installs a cloudFPGA addon (cFa) to an existing cFp

Options:
    -h --help       Show this screen.
    -v --version    Show version.
    
    --cfdk-version=<cfdkv>      Specifies that the cFDK can be accessed via Github and with cFDK-version should be used.
                                'latest' will use the latest available version.
    --git-url=<git-url>         Uses the given URL to clone cFDK instead the default.
    --cfdk-zip=<path-to-zip>    If the cFDK can't be reached via Github, a zip can be used.
    --git-init                  Creates the new cFp as git-repo; Adds the cFDK as git submodule, if not using a cfdk-zip
    --cfa-repo=<cfagit>         Link to the cFa git repository
    --cfa-zip=<path-to-zip>     Path to a cFa zip folder

Copyright IBM Research, All Rights Reserved.
Contact: {ngl,fab,wei}@zurich.ibm.com
```

There are three typical use-cases:
1. [Create a new project from scratch with an empty folder](#1-create-new-cloudfpga-project-cfp)
2. [Update an existing project, e.g. after a fresh clone or to switch Shell types](#2-update-an-existing-cfp)
3. [Beatify an existing project with an addon](#3-add-a-cloudfpga-addon-cfa-to-an-existing-cfp)


**General notice:** The terms *'git url'* or 'git repo' always refrer to a link that can be *used to clone the repository!*
E.g. `git@git.example.com:group/repo.git` or `https://git.example.com/group/repo.git`.
If *'a zip folder'* is mentioned, a zip-file provided by the cloudFPGA team is meant, so that it has the right structure etc.


### 1. Create new cloudFPGA project (cFp)

To create a new cFp, use the `cFBuild` command:

**The script will ask for the type of SRA or cF module --> see cFDK documentation.**
The `project-folder` should not exist (yet) or must be empty.

1. New cFp with a cFDK-zip
```bash
./cFBuild new --cfdk-zip=./<path>/cFDK-v0.1.zip <path-to-project-folder>
```
2. New cFp using cFDK from Github

```bash
./cFBuild new --cfdk-version=v0.1 <path-to-project-folder>
```

If the default Github URL is not accessible, an alternative can be specified with `-git-url`.

**The new project is initalized as git repository, if the option `--git-init` is used.**
In case of using cFDK from Github, this is initialized as git-submodule.
To init the project as git repository can also be done manually, see the section [Git integration](#git-integration) below.

### 2. Update an existing cFp

If it is necessary to regenerate the environment of the cFp (e.g. switch of SRA type or cFDK version,
 **or after a fresh clone of an existing cFp**), run:
```bash
./cFBuild update <path-to-project-folder> 
```

### 3. Add a cloudFPGA addon (cFa) to an existing cFp

Further features may be available outside the default cFDK. 
There are again two ways to install them to an existing cFp:

1. Using an existing git repository:
```bash
./cFBuild adorn --cfa-repo=<cfagit> <folder-name-for-addon> <path-to-project-folder>
```
2. Using a cFa-zip
```bash
./cFBuild adorn --cfa-zip=<path-to-zip> <folder-name-for-addon>  <path-to-project-folder>
```

The `<folder-name-for-addon>` will be the name of the folder that will be created in `<path-to-project-folder>` for the new cFa.


If the cFp is a git-repository, all changes will be commited by `cFBuild` (maybe check the output for error messages).
It is *not* necessary to run `cFBuild update` afterwards on any machine.


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
    <possible_addons/>
```


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

Git integration
--------------------

**If not done with the `--git-init` option** during the creation of a new cFp, 
the following steps are necessary to use the cFp as git repository and/or use the cFDK as git-submodule:

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

*(This could also be done by `cFBuild` with the `--git-init` option.)*

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

*(This could also be done by `cFBuild` with the `--git-init` option.)*


Known Limitations/Bugs
-----------------------

* Currently, only the non-PR flow (i.e. `monolithic`) is supported. Hence, it is recommended to:
  * create a cFp per Role
  * The `<cFp-repo>/ROLE/` should contain only one Role. 
  * Answer the question *Name of the (first) Role* with **`default`**.
* SRA `MPIv0_x2Mp_x2Mc` is currently broken
