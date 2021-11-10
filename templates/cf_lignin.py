# /*******************************************************************************
#  * Copyright 2016 -- 2021 IBM Corporation
#  *
#  * Licensed under the Apache License, Version 2.0 (the "License");
#  * you may not use this file except in compliance with the License.
#  * You may obtain a copy of the License at
#  *
#  *     http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
# *******************************************************************************/

#  *
#  *                       cloudFPGA
#  *    =============================================
#  *     Created: Nov 2021
#  *     Authors: FAB, WEI, NGL, DID
#  *
#  *     Description:
#  *       Python script to build and mange cloudFPGA projects (cFps).
#  *
#  *       The name is based on a very central polymers that form key
#  *       structural materials in the support tissues of most plants
#  *       (see further: https://en.wikipedia.org/wiki/Lignin).
#  *

import json
import os
import sys
from docopt import docopt
import re
from PyInquirer import prompt, print_json
from pprint import pprint

__version__ = 0.1

docstr = """Lignin -- cloudFPGA Project Build & Management Framework

Usage:
    lignin update-shell
    lignin config (add-role <path-to-role-dir> <name> | use-role <name> | del-role <name>)
    lignin build (proj | monolithic | pr) [role=<name>] [incr] [debug] 
    lignin clean [full]
    lignin admin (build (pr_full | pr_flash) | full_clean)
    
    lignin -h|--help
    lignin -v|--version

Commands:
    update-shell    Checks for a new static DCP of the selected shell and downloads it if necessary.
    config          Changes the project configuration (cFp.json) by adding, deleting and selecting Roles.
    build           Builds a new FPGA design, if not specified otherwise, the last selected/activated Role will be used.
    clean           Deletes temporary build files.
    admin           Provide additional commands for cFDK Shell developers.

Options:
    -h --help       Show this screen.
    -v --version    Show version.
    
    add-role <path-to-role-dir> <name>   Adds a new Role to the project configuration (cFp.json), to be used for builds.
    use-role <name>                      Sets the specified Role as active. Only one Role can be active at a time, so
                                         the previous activated Role will be deactivated. By default, the activated Role
                                         will be used for the build process.
    del-role <name>                      Deletes a Role from the configuration, it wil *not* delete files.

    proj                                 Create only the Vivado project files for a monolithic build and exit (useful if
                                         one wants to use the Vivado GUI).
    monolithic                           Invokes the `monolithic` build flow, using the activated Role.
    pr                                   Invokes the  `pr` (partial reconfiguration) build flow, using the activated
                                         Role and the latest downloaded static DCP (downloads a new DCP, if none is 
                                         present).
    role=<name>                          Uses the specified Role for the build process, not the current active Role.
    incr                                 Enables the incremental build feature for monolithic designs.
    debug                                Adds debug probes during the build process, as specified in `TOP/debug.xdc`.
    
    full                                 Makes a full clean, also removing generated HLS cores from the IP library.

Copyright IBM Research, licensed under the Apache License 2.0.
Contact: {ngl,fab,wei, did}@zurich.ibm.com
"""


def main():
    arguments = docopt(docstr, version=__version__)


if __name__ == '__main__':
    # vitrualenv is activated by the bash script
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        # This works with virtualenv for Python 3 and 2 and also for the venv module in Python 3
        print("ERROR: It looks like this cFCreate isn't running in a virtual environment. STOP.")
        sys.exit(1)
    main()
    exit(0)

