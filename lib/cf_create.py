# /*******************************************************************************
#  * Copyright 2016 -- 2022 IBM Corporation
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
#  *     Created: Apr 2019
#  *     Authors: FAB, WEI, NGL, DID
#  *
#  *     Description:
#  *       Python framework to create new cloudFPGA projects (cFp).
#  *

from __future__ import print_function, unicode_literals

import json
import os
import sys
from docopt import docopt
import re
from PyInquirer import prompt, print_json
from pprint import pprint

__version__ = 0.8

docstr = """cloudFPGA Project Creation Framework
cfBuild creates or updates cloudFPGA projects (cFp) based on the cloudFPGA Development Kit (cFDK).

Usage: 
    cFCreate new (--cfdk-version=<cfdkv> | --cfdk-zip=<path-to-zip>)  [--git-url=<git-url>] [--git-init] <path-to-project-folder>
    cFCreate update  <path-to-project-folder>
    cFCreate upgrade (--cfdk-version=<cfdkv> | --cfdk-zip=<path-to-zip>)  [--git-url=<git-url>] <path-to-project-folder>
    cFCreate adorn (--cfa-repo=<cfagit> | --cfa-zip=<path-to-zip>) <folder-name-for-addon> <path-to-project-folder>
    
    cFCreate -h|--help
    cFCreate -v|--version

Commands:
    new             Creates a new cFp based on the given cFDK
    update          Update the environment setting of an existing cFp
    upgrade         Upgrades the cFDK and the environment setting an existing cFp
    adorn           Installs a cloudFPGA addon (cFa) to an existing cFp

Options:
    -h --help       Show this screen.
    -v --version    Show version.
    
    --cfdk-version=<cfdkv>      Specifies that the cFDK can be accessed via Github and which cFDK-version should be used.
                                'latest' will use the latest available version.
    --git-url=<git-url>         Uses the given URL to clone cFDK instead the default.
    --cfdk-zip=<path-to-zip>    If the cFDK can't be reached via Github, a zip can be used.
    --git-init                  Creates the new cFp as git-repo; Adds the cFDK as git submodule, if not using a cfdk-zip
    --cfa-repo=<cfagit>         Link to the cFa git repository
    --cfa-zip=<path-to-zip>     Path to a cFa zip folder

Copyright IBM Research, licensed under the Apache License 2.0.
Contact: {ngl,fab,wei, did, hle}@zurich.ibm.com
"""

config_default_cfdk_url = "git@github.ibm.com:cloudFPGA/cFDK.git"
__me_abs_dir__ = os.path.dirname(os.path.realpath(__file__))
config_template_folder = os.path.abspath(__me_abs_dir__ + '/../templates')

DEFAULT_MOD = "FMKU60"
DEFAULT_SRA = "Themisto"
__env_file_name__ = "this_machine_env.sh"
__version_string__ = "This cFp was created by cFCreate " + str(__version__)
__to_be_defined_key__ = 'to-be-defined'
__sra_tool_key__ = 'srat-conf'

default_questions = [
    {
        'type': 'list',
        'name': 'cf_mod',
        'message': 'Which cloudFPGA module should be used in this project',
        'choices': ['FMKU60'],
    },
    {
        'type': 'list',
        'name': 'cf_sra',
        'message': 'Which Shell-Role Interface should be used in this project',
        # 'choices': ['x1Udp_x1Tcp_x2Mp_x2Mc', 'MPIv0_x2Mp_x2Mc'],
        'choices': ['x1Udp_x1Tcp_x2Mp_x2Mc'],
    },
    # {
    #     'type': 'confirm',
    #     'name': 'multipleRoles',
    #     'message': 'Do you plan to create multiple ROLEs for this project?',
    #     'default': False
    # },
    # {
    #     'type': 'input',
    #     'name': 'roleName1',
    #     'message': 'Name of the (first) Role (no spaces etc.):',
    #     'default': 'default',
    #     'filter': lambda val: val.split()[0]
    # },
]

vivado_question = {
    'type': 'input',
    'name': 'xilinx_settings',
    'message': 'The command \'vivado\' is not in the default \'$PATH\'. Please specify the path to the Xilinx environments:',
    'default': '/opt/xilinx/Vivado/2019.2/settings64.sh'
}

# pr_questions = [
#     {
#         'type': 'input',
#         'name': 'usedRoleDir',
#         'message': 'Directory name of the first Role (no spaces etc.):',
#         'default': 'V1',
#         'filter': lambda val: val.split()[0]
#     },
#     {
#         'type': 'input',
#         'name': 'roleName2',
#         'message': 'Name of the second Role (no spaces etc.):',
#         'default': 'V2',
#         'filter': lambda val: val.split()[0]
#     },
#     {
#         'type': 'input',
#         'name': 'usedRoleDir2',
#         'message': 'Directory name of the second Role (no spaces etc.):',
#         'default': 'V2',
#         'filter': lambda val: val.split()[0]
#     },
# ]

# TODO: deactivated for the moment, hard to do machine independent
# __xilinx_cmd_key__ = "xilinx_cmd"

# TODO: deactivated for the moment
# __match_regex__ = []
# __replace_regex__ = []
#
# __match_regex__.append("##SOURCE_VIVADO##")
# __replace_regex__.append(__xilinx_cmd_key__)
#
# __match_regex__.append("##ROOTDIR##")
# __replace_regex__.append("abs_path")
#
# __match_regex__.append("##MOD##")
# __replace_regex__.append("cf_mod")
#
# __match_regex__.append("##SRA##")
# __replace_regex__.append("cf_sra")
#
# __match_regex__.append("##DIR1##")
# __replace_regex__.append("usedRoleDir")
#
# __match_regex__.append("##DIR2##")
# __replace_regex__.append("usedRoleDir2")
#
# __match_regex__.append("##ROLE1##")
# __replace_regex__.append("roleName1")
#
# __match_regex__.append("##ROLE2##")
# __replace_regex__.append("roleName2")
#
# __match_regex__.append("##virtual_path##")
# __replace_regex__.append("cfenvPath")
#
# __match_regex__.append("##python3_bin##")
# __replace_regex__.append("sysPython3Bin")

__SRA_config_keys__ = []
__SRA_config_keys__.append("additional_lines")  # must be at position 0!
__SRA_config_keys__.append(__sra_tool_key__)

__json_backup_keys__ = []
__json_backup_keys__.append("additional_lines")
__json_backup_keys__.append(__sra_tool_key__)


def create_cfp_dir_structure(folder_path):
    os.system("mkdir -p {}/TOP/tcl".format(folder_path))
    os.system("mkdir -p {}/TOP/hdl".format(folder_path))
    os.system("mkdir -p {}/TOP/xdc".format(folder_path))
    os.system("echo 'keep' > {}/TOP/xdc/.gitkeep".format(folder_path))
    os.system("mkdir -p {}/ROLE/".format(folder_path))
    os.system("mkdir -p {}/env/".format(folder_path))


def checkout_cfdk(cfdk_tag, cfdk_zip, folder_path, git_url=None, git_init=False):
    if cfdk_zip is not None:
        rc = os.system("unzip {} -d {}".format(cfdk_zip, folder_path))
        if rc != 0:
            return "ERROR: Failed to unzip cFDK", -1
    else:  # use git
        if git_url is None:
            git_url = config_default_cfdk_url

        tag_str = ""
        git_checkout_version = False
        if cfdk_tag != "latest":
            tag_str = "-b '{}'".format(cfdk_tag)
            git_checkout_version = True
        if git_init:
            rc = os.system("cd {}; git submodule add -f {} ./cFDK/".format(folder_path, git_url))
            if rc != 0:
                return "ERROR: Failed to init submodule cFDK", -1
            if git_checkout_version:
                os.system("cd {}/cFDK/; git checkout {}".format(folder_path, tag_str))
                # no error handling for now
        else:
            rc = os.system("git clone {} --single-branch --depth 1 {} {}/cFDK/".format(tag_str, git_url, folder_path))
            if rc != 0:
                return "ERROR: Failed to checkout cFDK", -1
    return "", 0


def create_new_cfp(cfdk_tag, cfdk_zip, folder_path, git_url=None, git_init=False):
    if cfdk_tag is None and cfdk_zip is None:
        return "ERROR: Missing mandatory arguments", -2

    os.system("mkdir -p {}".format(folder_path))

    if git_init:
        os.system("git init {}".format(folder_path))

    msg, rc = checkout_cfdk(cfdk_tag, cfdk_zip, folder_path, git_url, git_init)
    if rc != 0:
        return msg, rc

    create_cfp_dir_structure(folder_path)

    # copy templates that should be copied only during create
    os.system("cp {0}/gitignore.template {1}/.gitignore".format(config_template_folder, folder_path))
    os.system("cp {0}/cfdk_Makefile {1}/Makefile".format(config_template_folder, folder_path))

    return "", 0


def upgrade_existing_cfdk(cfdk_tag, cfdk_zip, folder_path, git_url=None):
    if cfdk_tag is None and cfdk_zip is None:
        return "ERROR: Missing mandatory arguments", -2

    folder_abspath = os.path.abspath(folder_path)
    use_git_flow = False
    if os.path.isdir("{}/.git".format(folder_abspath)):
        use_git_flow = True

    # cleanup old cFDK
    if use_git_flow:
        rc = os.system("cd {}; git config -f .git/config --remove-section submodule.cFDK".format(folder_abspath))
        if rc != 0:
            return "ERROR: Failed to remove old cFDK submodule", -1
        rc = os.system("cd {}; git config -f .gitmodules --remove-section submodule.cFDK".format(folder_abspath))
        if rc != 0:
            return "ERROR: Failed to remove old cFDK submodule", -1
        rc = os.system("cd {}; git rm --cached cFDK".format(folder_abspath))
        if rc != 0:
            return "ERROR: Failed to remove old cFDK submodule", -1
        rc = os.system("cd {}; rm -rf .git/modules/cFDK".format(folder_abspath))
        if rc != 0:
            return "ERROR: Failed to remove old cFDK submodule", -1
    # in all cases
    rc = os.system("cd {}; rm -rf cFDK".format(folder_abspath))
    if rc != 0:
        return "ERROR: Failed to remove old cFDK folder", -1

    msg, rc = checkout_cfdk(cfdk_tag, cfdk_zip, folder_path, git_url, git_init=use_git_flow)
    if rc != 0:
        return msg, rc

    if use_git_flow:
        os.system("cd {}; git commit -m'[cFCreate] clean-up and upgrade of cFDK'".format(folder_abspath))
    return "", 0


def prepare_questions(folder_path, additional_defaults=None):
    # check vivado path
    questions = []

    # TODO: deactivated for the moment, hard to do machine independent
    # rc = os.system("vivado -version  > /dev/null 2>&1")
    # if rc != 0:
    #     questions.append(vivado_question)

    mods_available = []
    mod_default = 0
    sra_available = []
    sra_default = 0

    subfolders = [f.name for f in os.scandir("{}/cFDK/SRA/LIB/SHELL".format(folder_path)) if f.is_dir()]
    i = 0
    for f in subfolders:
        if f != "LIB":
            sra_available.append(f)
            if f == DEFAULT_SRA:
                sra_default = i
            i += 1

    subfolders = [f.name for f in os.scandir("{}/cFDK/MOD".format(folder_path)) if f.is_dir()]
    i = 0
    for f in subfolders:
        mods_available.append(f)
        if f == DEFAULT_MOD:
            mod_default = i
        i += 1

    # questions.extend(default_questions)
    for q in default_questions:
        if q['name'] == 'cf_mod':
            q['choices'] = mods_available
            q['default'] = mod_default  # TODO: default seems to be ignored...
        if q['name'] == 'cf_sra':
            q['choices'] = sra_available
            q['default'] = sra_default  # TODO: default seems to be ignored...
        if additional_defaults is not None:
            for k in additional_defaults:
                if q['name'] == k:
                    q['default'] = additional_defaults[k]
        questions.append(q)

    return questions


def get_python_envs():
    # on this machine, that's fine
    cfenv_path = os.environ['VIRTUAL_ENV']

    # this is not working, we need the python3 without the virutalenv
    # sys_py_bin = os.popen('which python3').read()
    sys_py_bin = None
    if 'cFsysPy3_cmd_hint_0' in os.environ and os.path.isfile(os.environ['cFsysPy3_cmd_hint_0']):
        sys_py_bin = os.environ['cFsysPy3_cmd_hint_0']
    elif 'cFsysPy3_cmd_hint_1' in os.environ and os.path.isfile(os.environ['cFsysPy3_cmd_hint_1']):
        sys_py_bin = os.environ['cFsysPy3_cmd_hint_1']
    elif os.path.isfile('/usr/bin/python3.8'):
        sys_py_bin = '/usr/bin/python3.8'
    elif os.path.isfile('/usr/bin/python3'):
        sys_py_bin = '/usr/bin/python3'
    else:
        # as fallback, better than nothing
        # returns the virtualenv python
        sys_py_bin = os.popen('which python3').read()
    return cfenv_path, sys_py_bin


def create_json(folder_path, envs):
    json_data = {}
    json_data['version'] = __version_string__
    json_data['cFpMOD'] = envs['cf_mod']
    json_data['cFpSRAtype'] = envs['cf_sra']
    json_data['usedRoleDir'] = envs['usedRoleDir']
    json_data['usedRoleDir2'] = envs['usedRoleDir2']
    json_data['roleName1'] = envs['roleName1']
    json_data['roleName2'] = envs['roleName2']
    if 'additional_lines' in envs:
        json_data['additional_lines'] = envs['additional_lines']

    with open("{}/cFp.json".format(folder_path), "w+") as json_file:
        json.dump(json_data, json_file, indent=4)


def update_json(folder_path, new_entries=None, update_list=None):
    with open("{}/cFp.json".format(folder_path), "r") as json_file:
        data = json.load(json_file)

    if new_entries is not None:
        for e in new_entries:
            data[e] = new_entries[e]
    if update_list is not None:
        for e in update_list:
            if e in data.keys():
                if type(data[e]) is list:
                    new_list = data[e]
                    new_list.extend(update_list[e])
                    data[e] = list(set(new_list))
                elif type(data[e]) is dict:
                    data[e].update(update_list[e])
                else:
                    print("Warning: forced to overwrite config parameter {} (previous value {})".format(e, data[e]))
                    data[e] = update_list[e]
            else:
                # data[e] = list(set(update_list[e]))
                data[e] = update_list[e]

    # in all cases, update the version
    data['version'] = __version_string__

    with open("{}/cFp.json".format(folder_path), "w") as json_file:
        json.dump(data, json_file, indent=4)


def copy_templates_and_set_env(folder_path, envs, backup_json=False):
    additional_envs = {}
    if backup_json:
        json_path = "{}/cFp.json".format(folder_path)
        if os.path.exists(json_path):
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
            for k in __json_backup_keys__:
                if k in data.keys():
                    additional_envs[k] = data[k]

    os.system("cp {0}/cFDK/SRA/LIB/TOP/{1}/top.vhdl {0}/TOP/hdl/top.vhdl".format(
        folder_path, envs['cf_sra']))

    json_extend = False
    config_file = "{0}/cFDK/SRA/LIB/TOP/{1}/config.json".format(
        folder_path, envs['cf_sra'])
    if os.path.exists(config_file):
        with open(config_file, 'r') as json_file:
            data = json.load(json_file)
        for k in __SRA_config_keys__:
            if k in data.keys():
                json_extend = True
                if k in additional_envs.keys():
                    additional_envs[k].extend(data[k])
                else:
                    additional_envs[k] = data[k]

    # check for xilinx cmd
    # if __xilinx_cmd_key__ in envs:
    #     if __SRA_config_keys__[0] not in additional_envs:
    #         additional_envs[__SRA_config_keys__[0]] = []
    #     additional_envs[__SRA_config_keys__[0]].append(envs[__xilinx_cmd_key__])
    #     json_extend = True

    # update tcl (Makefile only during create, just to not overwrite cFa's)
    os.system("cp -Rf {0}/cFDK/SRA/LIB/TOP/tcl/ {0}/TOP/".format(folder_path))

    # env_file = "{}/env/setenv.sh".format(folder_path)
    env_file = "{}/env/{}".format(folder_path, __env_file_name__)
    # just to be sure...
    os.system("mkdir -p {}/env/".format(folder_path))

    # copy cFp kit
    os.system("cp {}/machine_env.template {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/gen_env.py {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/setenv.sh {}/env/".format(config_template_folder, folder_path))
    os.system("chmod +x {}/env/setenv.sh".format(folder_path))
    os.system("chmod +x {}/env/gen_env.py".format(folder_path))
    os.system("cp {}/create_sig.py {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/create_sig.sh {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/admin_sig.py {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/admin_sig.sh {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/get_latest_dcp.py {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/cf_sratool.py {}/env/".format(config_template_folder, folder_path))
    os.system("cp {}/sra {}/".format(config_template_folder, folder_path))
    os.system("chmod +x {}/sra".format(folder_path))

    if os.path.isdir(folder_path + '.git/'):
        # git config, add new files
        os.system("cd {}; git add sra env/".format(folder_path))

    create_json(folder_path, envs)
    if json_extend or backup_json:
        update_json(folder_path, update_list=additional_envs)
    # now, load new data
    with open("{}/cFp.json".format(folder_path), "r") as json_file:
        cfp_data = json.load(json_file)
    envs.update(cfp_data)

    # adding python env
    cfenv_path, sys_py_bin = get_python_envs()
    envs['cfenvPath'] = cfenv_path
    envs['sysPython3Bin'] = sys_py_bin

    # TODO: deactivated for the moment, is done by sra tool anyhow (and better)
    # with open("{}/machine_env.template".format(config_template_folder), "r") as input, open(env_file, "w") as outfile:
    #     out = input.read()
    #     for i in range(0, len(__match_regex__)):
    #         out = re.sub(re.escape(__match_regex__[i]), envs[__replace_regex__[i]], out)
    #     outfile.write(out)
    # os.system("chmod +x {}".format(env_file))

    return 0


def install_cfa(folder_path, addon_name, git_url=None, zip_path=None):
    if git_url is None and zip_path is None:
        return "ERROR: Missing mandatory arguments", 1

    folder_abspath = os.path.abspath(folder_path)

    if zip_path is not None:
        rc = os.system("unzip {} -d {}/{}/".format(zip_path, folder_abspath, addon_name))
        if rc != 0:
            return "ERROR: Failed to unzip cFa", 1
    else:  # use git
        rc = os.system("cd {}; git submodule add -f {} ./{}/".format(folder_abspath, git_url, addon_name))
        if rc != 0:
            return "ERROR: Failed to add submodule cFa", 1

    # execute setup script
    cmd_str = "/bin/bash -c \"source {}/env/setenv.sh && {}/{}/install/setup.sh '{}'\"".format(folder_abspath,
                                                                                               folder_abspath,
                                                                                               addon_name, addon_name)
    print(cmd_str)
    rc = os.system(cmd_str)
    if rc != 0:
        return "ERROR: Failed to setup cFa", 1

    update_json_data = {}
    update_json_data['additional_lines'] = ['export {}Dir="$rootDir/{}/"'.format(addon_name.lower(), addon_name)]
    update_json_data['cFa'] = [str(addon_name)]
    # update_json(folder_path, update_json_data)
    update_json(folder_path, update_list=update_json_data)

    # commit changes if it is a git
    os.system("[ -d {}/.git/ ] && (cd {}; git add ./{}/ ;git commit -a -m'Installed cFa {}')".format(
        folder_abspath, folder_abspath, addon_name, addon_name))

    return "SUCCESSfully added cFa {}!".format(addon_name), 0


def main():
    arguments = docopt(docstr, version=__version__)

    folder_path = arguments['<path-to-project-folder>']
    # if folder_path[-1] == '/':
    #    # to remove / to prevent //
    #    folder_path = folder_path[:-1]

    also_do_update = False
    if arguments['new']:
        msg, rc = create_new_cfp(arguments['--cfdk-version'], arguments['--cfdk-zip'], folder_path,
                                 git_url=arguments['--git-url'], git_init=arguments['--git-init'])
        if rc != 0:
            print(msg)
            exit(1)
    elif arguments['adorn']:
        msg, rc = install_cfa(folder_path, arguments['<folder-name-for-addon>'], git_url=arguments['--cfa-repo'],
                              zip_path=arguments['--cfa-zip'])
        print(msg)
        exit(rc)
    elif arguments['upgrade']:
        msg, rc = upgrade_existing_cfdk(arguments['--cfdk-version'], arguments['--cfdk-zip'], folder_path,
                                        git_url=arguments['--git-url'])
        if rc != 0:
            print(msg)
            exit(1)
        also_do_update = True

    question_defaults = None
    if arguments['update'] or also_do_update:
        json_path = "{}/cFp.json".format(folder_path)
        if os.path.exists(json_path):
            question_defaults = {}
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
            if "roleName1" in data.keys():
                question_defaults['roleName1'] = data['roleName1']
            if "roleName2" in data.keys():
                question_defaults['roleName2'] = data['roleName2']
            if "usedRoleDir" in data.keys():
                question_defaults['usedRoleDir'] = data['usedRoleDir']
            if "usedRoleDir2" in data.keys():
                question_defaults['usedRoleDir2'] = data['usedRoleDir2']

    questions = prepare_questions(folder_path, additional_defaults=question_defaults)
    answers = prompt(questions)
    answers_pr = {}
    # if answers['multipleRoles']:
    #     custom_pr_questions = []
    #     if question_defaults is not None:
    #         for q in pr_questions:
    #             for k in question_defaults:
    #                 if q['name'] == k:
    #                     q['default'] = question_defaults[k]
    #             custom_pr_questions.append(q)
    #     else:
    #         custom_pr_questions = pr_questions
    #     answers_pr = prompt(custom_pr_questions)
    #     if answers_pr['usedRoleDir'][-1] != '/':
    #         answers_pr['usedRoleDir'] += "/"
    #     if answers_pr['usedRoleDir2'][-1] != '/':
    #         answers_pr['usedRoleDir2'] += "/"
    # else:
    #     answers_pr['usedRoleDir'] = ""
    #     answers_pr['usedRoleDir2'] = ""
    #     answers_pr['roleName2'] = "unused"
    # for now, the role setting is managed by sra-tool
    answers_pr['roleName1'] = 'default'
    answers_pr['usedRoleDir'] = ''  # default
    answers_pr['roleName2'] = __to_be_defined_key__
    answers_pr['usedRoleDir2'] = __to_be_defined_key__

    envs = {**answers, **answers_pr}

    # TODO: deactivated for the moment, hard to do machine independent
    # if 'xilinx_settings' not in envs:
    #     envs[__xilinx_cmd_key__] = ""
    # else:
    #     # envs['xilinx_cmd'] = "source " + envs['xilinx_settings'] + "\n"
    #     envs[__xilinx_cmd_key__] = "source " + envs['xilinx_settings'] + "\n"
    #     # save it for later
    #     if 'additional_lines' not in envs:
    #         envs['additional_lines'] = []
    #     envs['additional_lines'].append(envs[__xilinx_cmd_key__])
    envs['abs_path'] = os.path.abspath(folder_path)
    # pprint(envs)

    backup_json = False
    if arguments["update"]:
        backup_json = True

    copy_templates_and_set_env(folder_path, envs, backup_json=backup_json)

    if arguments['--git-init']:
        os.system("cd {}; git add .; git commit -m'cFp init by cFCreate'".format(folder_path))
        print("To complete the git repository initialization execute: \n" +
              "\t$ git remote add origin <remote-repository-URL>\n" +
              "\t$ git push origin master\n")

    print("SUCCESS!\ncloudFPGA project in {} ready to use!".format(envs['abs_path']) +
          "\nDon't forget to `source env/setenv.sh`")

    # srat_fyi = "\npsst...just FYI: If you want to use the new 'sra' command without typing always " \
    #            "'./' first, \nyou can add the following to your '~/.bashrc' and activate it with 'source ~/.bashrc' " \
    #            "afterwards:\n"
    # srat_bashrc = '--------------\n'\
    #               'srafunc(){\n\tcur_pwd=$(pwd)\n\tsrat=$cur_pwd/sra\n\tif [ -f "$srat" ]; then\n\t\t$srat $@\n\telse' \
    #               '\n\t\techo "Error: No cloudFPGA sra tools present in this folder."\n\tfi\n}\n\nalias sra=srafunc\n'\
    #               '--------------\n'
    # if 'cFpSraToolAliasIsPresent' not in os.environ:
    #     print(srat_fyi + srat_bashrc)


if __name__ == '__main__':
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        # This works with virtualenv for Python 3 and 2 and also for the venv module in Python 3
        print("ERROR: It looks like this cFCreate isn't running in a virtual environment. STOP.")
        sys.exit(1)
    main()
    exit(0)
