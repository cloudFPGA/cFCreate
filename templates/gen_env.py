#!/usr/bin/env python3
# /*******************************************************************************
#  * Copyright 2016 -- 2020 IBM Corporation
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
#  *     Created: FEB 2020
#  *     Authors: FAB, WEI, NGL
#  *
#  *     Description:
#  *       Python file to parse cFp.json
#  *

import json
import os
import re

__cfp_json_path__ = "/../cFp.json"
__env_file_name__ = "/this_machine_env.sh"

__mandatory_keys__ = ['cFpMOD', 'usedRoleDir', 'usedRoleDir2', 'cFpSRAtype', 'roleName1', 'roleName2',
                      'cfenvPath', 'sysPython3Bin']
__optional_keys__ = ['cFa', 'additional_lines']

__match_regex__ = []
__replace_regex__ = []

__match_regex__.append("##ROOTDIR##")
__replace_regex__.append("abs_path")

__match_regex__.append("##MOD##")
__replace_regex__.append("cFpMOD")

__match_regex__.append("##SRA##")
__replace_regex__.append("cFpSRAtype")

__match_regex__.append("##DIR1##")
__replace_regex__.append("usedRoleDir")

__match_regex__.append("##DIR2##")
__replace_regex__.append("usedRoleDir2")

__match_regex__.append("##ROLE1##")
__replace_regex__.append("roleName1")

__match_regex__.append("##ROLE2##")
__replace_regex__.append("roleName2")

__match_regex__.append("##virtual_path##")
__replace_regex__.append("cfenvPath")

__match_regex__.append("##python3_bin##")
__replace_regex__.append("sysPython3Bin")


def print_incomplete(msg=""):
    me_abs = os.path.realpath(__file__)
    cfp_json_file = os.path.abspath(me_abs + __cfp_json_path__)
    print("The project describing file {} is invalid.\n{}\n".format(cfp_json_file, msg) +
          "Please use 'cFBuild update' to fix this project setup.")
    exit(1)


def main():
    me_abs = os.path.dirname(os.path.realpath(__file__))
    cfp_json_file = me_abs + __cfp_json_path__
    with open(cfp_json_file, 'r') as json_file:
        data = json.load(json_file)

    root_abs = os.path.realpath(me_abs+"/../")
    data['abs_path'] = root_abs

    for e in __mandatory_keys__:
        if e not in data.keys():
            print_incomplete("The mandatory key {} is missing.".format(e))

    env_file = me_abs + __env_file_name__

    # first, check the timestamps
    if os.path.exists(env_file):
        json_time = os.path.getmtime(cfp_json_file)
        env_time = os.path.getmtime(env_file)

        if env_time >= json_time:
            # the environment was already created...nothing to do
            exit(0)

    with open(me_abs + "/machine_env.template", "r") as input, open(env_file, "w+") as outfile:
        out = input.read()
        for i in range(0, len(__match_regex__)):
            out = re.sub(re.escape(__match_regex__[i]), data[__replace_regex__[i]], out)

        if 'additional_lines' in data.keys():
            out += '\n\n'
            for e in data['additional_lines']:
                new_line = str(e) + '\n'
                out += new_line
            out += '\n\n'

        outfile.write(out)

    os.system("chmod +x {}".format(env_file))


if __name__ == '__main__':
    main()
    exit(0)

