#  *
#  *                       cloudFPGA
#  *     Copyright IBM Research, All Rights Reserved
#  *    =============================================
#  *     Created: Apr 2019
#  *     Authors: FAB, WEI, NGL
#  *
#  *     Description:
#  *       Python framework to create new cloudFPGA projects (cFp).
#  *

from __future__ import print_function, unicode_literals
import os
import sys
from docopt import docopt
import re
from PyInquirer import prompt, print_json
from pprint import pprint

docstr="""cloudFPGA Build Framework
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
"""

cfdk_url = "git@github.ibm.com:cloudFPGA/cFDK.git"
#cfdk_url = "https://github.ibm.com/cloudFPGA/cFDK.git"

DEFAULT_MOD = "FMKU60"
DEFAULT_SRA = "x1Udp_x1Tcp_x2Mp_x2Mc"

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
    # TODO
    # {
    #     'type': 'confirm',
    #     'name': 'copyRole',
    #     'message': 'Should the RoleEchoHls-Template be copied as ROLE',
    #     'default': False
    # },
    {
        'type': 'confirm',
        'name': 'multipleRoles',
        'message': 'Do you plan to create multiple ROLEs for this project?',
        'default': False
    },
    {
        'type': 'input',
        'name': 'role_name_1',
        'message': 'Name of the (first) Role (no spaces etc.):',
        'default': 'default',
        'filter': lambda val: val.split()[0]
    },
]

vivado_question = {
    'type': 'input',
    'name': 'xilinx_settings',
    'message': 'The command \'vivado\' is not in the default \'$PATH\'. Please specify the path to the Xilinx environments:',
    'default': '/opt/Xilinx/Vivado/2017.4/settings64.sh'
}

pr_questions = [
    {
        'type': 'input',
        'name': 'role_dir_1',
        'message': 'Directory name of the first Role (no spaces etc.):',
        'default': 'V1',
        'filter': lambda val: val.split()[0]
    },
    {
        'type': 'input',
        'name': 'role_name_2',
        'message': 'Name of the second Role (no spaces etc.):',
        'default': 'V2',
        'filter': lambda val: val.split()[0]
    },
    {
        'type': 'input',
        'name': 'role_dir_2',
        'message': 'Directory name of the second Role (no spaces etc.):',
        'default': 'V2',
        'filter': lambda val: val.split()[0]
    },
]

__match_regex__ = []
__replace_regex__ = []

__match_regex__.append("##SOURCE_VIVADO##")
__replace_regex__.append("xilinx_cmd")

__match_regex__.append("##ROOTDIR##")
__replace_regex__.append("abs_path")

__match_regex__.append("##MOD##")
__replace_regex__.append("cf_mod")

__match_regex__.append("##SRA##")
__replace_regex__.append("cf_sra")

__match_regex__.append("##DIR1##")
__replace_regex__.append("role_dir_1")

__match_regex__.append("##DIR2##")
__replace_regex__.append("role_dir_2")

__match_regex__.append("##ROLE1##")
__replace_regex__.append("role_name_1")

__match_regex__.append("##ROLE2##")
__replace_regex__.append("role_name_2")


def create_cfp_dir_structure(folder_path):
    os.system("mkdir -p {}/TOP/tcl".format(folder_path))
    os.system("mkdir -p {}/TOP/hdl".format(folder_path))
    os.system("mkdir -p {}/TOP/xdc".format(folder_path))
    os.system("mkdir -p {}/ROLE/".format(folder_path))
    os.system("mkdir -p {}/env/".format(folder_path))


def create_new_cfp(cfdk_tag, cfdk_zip, folder_path, git_url=None):
    if cfdk_tag is None and cfdk_zip is None:
        return "ERROR: Missing manadtory arguments", -2

    os.system("mkdir -p {}".format(folder_path))

    if cfdk_zip is not None:
        rc = os.system("unzip {} -d {}".format(cfdk_zip, folder_path))
        if rc != 0:
            return "ERROR: Failed to unzip cFDK", -1
    else:  # use git
        if git_url is None:
            git_url=cfdk_url

        tag_str = ""
        if cfdk_tag != "latest":
            tag_str = "-b '{}'".format(cfdk_tag)
        rc = os.system("git clone {} --single-branch --depth 1 {} {}/cFDK/".format(tag_str, git_url, folder_path))
        if rc !=0:
            return "ERROR: Failed to checkout cFDK", -1

    create_cfp_dir_structure(folder_path)

    os.system("cp ./lib/gitignore.template {0}/.gitignore".format(folder_path))

    return "", 0


def prepare_questions(folder_path):
    # check vivado path
    questions = []
    rc = os.system("vivado -version  > /dev/null 2>&1")
    if rc != 0:
        questions.append(vivado_question)

    mods_available = []
    mod_default = 0
    sra_available = []
    sra_default = 0

    subfolders = [f.name for f in os.scandir("{}/cFDK/SRA/LIB/SHELL".format(folder_path)) if f.is_dir() ]
    i = 0
    for f in subfolders:
        if f != "LIB":
            sra_available.append(f)
            if f == DEFAULT_SRA:
                sra_default = i
            i += 1

    subfolders = [f.name for f in os.scandir("{}/cFDK/MOD".format(folder_path)) if f.is_dir() ]
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
        questions.append(q)

    return questions


def copy_templates_and_set_env(folder_path, envs):

    os.system("cp {0}/cFDK/MOD/{1}/hdl/top_{2}.vhdl.template {0}/TOP/hdl/top.vhdl".format(
        folder_path, envs['cf_mod'], envs['cf_sra']))

    # update tcl  and Makefiles, too
    os.system("cp -Rf {0}/cFDK/SRA/LIB/TOP/tcl/ {0}/TOP/".format(folder_path))
    os.system("cp {0}/cFDK/SRA/LIB/TOP/Makefile.template {0}/Makefile".format(folder_path))

    env_file = "{}/env/setenv.sh".format(folder_path)

    with open("./lib/setenv.template", "r") as input, open(env_file, "w") as outfile:
        out = input.read()
        for i in range(0, len(__match_regex__)):
            out = re.sub(re.escape(__match_regex__[i]), envs[__replace_regex__[i]], out)

        outfile.write(out)

    os.system("chmod +x {}".format(env_file))

    return 0


def main():
    arguments = docopt(docstr, version='0.1')

    folder_path = arguments['<path-to-project-folder>']
    if arguments['new']:
        msg, rc = create_new_cfp(arguments['--cfdk-version'], arguments['--cfdk-zip'], folder_path, git_url=arguments['--git-url'])
        if rc != 0:
            print(msg)
            exit(1)

    questions = prepare_questions(folder_path)
    answers = prompt(questions)
    answers_pr = {}
    if answers['multipleRoles']:
        answers_pr = prompt(pr_questions)
        answers_pr['role_dir_1'] += "/"
        answers_pr['role_dir_2'] += "/"
    else:
        answers_pr['role_dir_1'] = ""
        answers_pr['role_dir_2'] = ""
        answers_pr['role_name_2'] = "unused"

    envs = {**answers, **answers_pr}
    if 'xilinx_settings' not in envs:
        envs['xilinx_cmd'] = ""
    else:
        envs['xilinx_cmd'] = "source " + envs['xilinx_settings'] + "\n"
    envs['abs_path'] = os.path.abspath(folder_path)
    # pprint(envs)

    copy_templates_and_set_env(folder_path, envs)
    print("SUCCESS!\ncloudFPGA project in {} ready to use!".format(envs['abs_path']) +
          "\nDon't forget to `source env/setenv.sh`")


if __name__ == '__main__':
    main()
    exit(0)


