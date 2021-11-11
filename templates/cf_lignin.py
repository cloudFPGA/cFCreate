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

__version__ = 0.2

docstr = """Lignin -- cloudFPGA Project Build & Management Framework

Usage:
    lignin update-shell
    lignin config (add-role <path-to-role-dir> <name> | use-role <name> | del-role <name> | show )
    lignin build (proj | monolithic | pr) [--role=<name>] [--incr] [--debug] 
    lignin clean [--full]
    lignin admin (build (pr_full | pr_flash) | full_clean | set-2nd-role <name> | write-to-json)
    
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
                                         The <path-to-role-dir> *must* be within the <cFp-Root>/ROLE/ directory.
    use-role <name>                      Sets the specified Role as active. Only one Role can be active at a time, so
                                         the previous activated Role will be deactivated. By default, the activated Role
                                         will be used for the build process.
    del-role <name>                      Deletes a Role from the configuration, it wil *not* delete files.
    show                                 Show current project configuration.

    proj                                 Create only the Vivado project files for a monolithic build and exit (useful if
                                         one wants to use the Vivado GUI).
    monolithic                           Invokes the `monolithic` build flow, using the activated Role.
    pr                                   Invokes the  `pr` (partial reconfiguration) build flow, using the activated
                                         Role and the latest downloaded static DCP (downloads a new DCP, if none is 
                                         present).
    --role=<name>                        Uses the specified Role for the build process, not the current active Role.
    --incr                               Enables the incremental build feature for monolithic designs.
    --debug                              Adds debug probes during the build process, as specified in TOP/xdc/debug.xdc.
    
    --full                               Makes a full clean, also removing generated HLS cores from the IP library.

Copyright IBM Research, licensed under the Apache License 2.0.
Contact: {ngl,fab,wei, did, hle}@zurich.ibm.com
"""

__cfp_json_name__ = 'cFp.json'
__to_be_defined_key__ = 'to-be-defined'
__none_key__ = 'None'
__lignin_key__ = 'lignin-conf'
__role_config_dict_templ__ = {'name': "", 'path': ""}
__default_role_entry__ = {'name': 'default', 'path': ""}
__lignin_dict_template__ = {'version': __version__, 'roles': [__default_role_entry__],
                            'active_role': __to_be_defined_key__}
__admin_key__ = 'admin'
__admin_dict_template__ = {'2nd-role': __to_be_defined_key__}
__shell_type_key__ = 'cFpSRAtype'
__mod_type_key__ = 'cFpMOD'
__dcps_folder_name__ = '/dcps/'


def get_cfp_role_path(cfp_root, role_entry):
    role_path = os.path.abspath(cfp_root + '/ROLE/' + role_entry['path'])
    return role_path


def main():
    arguments = docopt(docstr, version=__version__)

    # first, get and parse cFp.json
    cfp_root = os.environ['cFpRootDir']
    cfp_env_folder = os.path.abspath(cfp_root + '/env/')
    cfenv_small_py_bin = os.path.abspath(cfp_root + 'env/cfenv-small/bin/python3.8')
    cfp_json_file = os.path.abspath(cfp_root + '/' + __cfp_json_name__)
    with open(cfp_json_file, 'r') as json_file:
        cFp_data = json.load(json_file)

    store_updated_cfp_json = False
    # check for structure
    if __lignin_key__ not in cFp_data:
        cFp_data[__lignin_key__] = __lignin_dict_template__
        store_updated_cfp_json = True

    if arguments['admin']:
        if __admin_key__ not in cFp_data[__lignin_key__]:
            cFp_data[__lignin_key__][__admin_key__] = __admin_dict_template__
            store_updated_cfp_json = True

    # check for used role 1
    if cFp_data['roleName1'] == __to_be_defined_key__:
        store_updated_cfp_json = True
        cFp_data['roleName1'] = 'default'
        cFp_data['usedRoleDir'] = ''  # default ROLE/ folder, no hierarchy

    dcps_folder = os.path.abspath(cfp_root + __dcps_folder_name__)
    dcp_file_name = "3_top{}_STATIC.dcp".format(cFp_data[__mod_type_key__])
    dcp_file_path = os.path.abspath(dcps_folder + "/" + dcp_file_name)
    meta_file_name = "3_top{}_STATIC.json".format(cFp_data[__mod_type_key__])
    meta_file_path = os.path.abspath(dcps_folder + "/" + meta_file_name)

    # print(arguments)
    # handle arguments
    # FIXME: I know, bad programming stile with endless indents instead of return...cleanup after first tests...
    if arguments['update-shell']:
        # os.system("{} {}/get_latest_dcp.py".format(os.environ['cFsysPy3_cmd'], cfp_env_folder))
        os.system("{} {}/get_latest_dcp.py".format(cfenv_small_py_bin, cfp_env_folder))
    elif arguments['clean']:
        if arguments['--full']:
            os.system('cd {}; make full_clean'.format(cfp_root))
        else:
            os.system('cd {}; make clean'.format(cfp_root))
    elif arguments['config']:
        if arguments['show']:
            print("[Lignin:INFO] The following roles are currently defined:")
            if len(cFp_data[__lignin_key__]['roles']) == 0:
                print("\tnone")
            else:
                for e in cFp_data[__lignin_key__]['roles']:
                    print("\tRole {} in directory {}".format(e['name'],
                                                             os.path.abspath(cfp_root + '/ROLE/' + e['path'])))
            if cFp_data[__lignin_key__]['active_role'] != __to_be_defined_key__:
                print("\tCurrent active role: {}".format(cFp_data[__lignin_key__]['active_role']))
        elif arguments['add-role']:
            relative_path = ''
            path_parts = arguments['<path-to-role-dir>'].split('/')
            for pp in path_parts:
                if len(pp) == 0:
                    break
                if pp == '.':
                    continue
                if pp == 'ROLE':
                    # maybe they specified it with relative path/tab completion
                    continue
                relative_path += pp + '/'  # must be there also for the last entry
            new_abs_path = os.path.abspath(cfp_root + '/ROLE/' + relative_path)
            if not os.path.isdir(new_abs_path):
                print("[ERROR] The specified path {} seems not to be a valid directory.".format(new_abs_path))
                print("\t(Hint: All roles for this project must be in/below the {} directory.)"
                      .format(os.path.abspath(cfp_root + '/ROLE/')))
            else:
                new_role_dict = {'name': arguments['<name>'], 'path': relative_path}
                does_exist = False
                for existing_entry in cFp_data[__lignin_key__]['roles']:
                    if existing_entry['name'] == new_role_dict['name']:
                        print("[Lignin:ERROR] A role with the name {} exists already.".format(new_role_dict['name']))
                        does_exist = True
                        break
                if not does_exist:
                    cFp_data[__lignin_key__]['roles'].append(new_role_dict)
                    store_updated_cfp_json = True
        elif arguments['use-role']:
            new_active_role = arguments['<name>']
            is_existing = False
            for existing_entry in cFp_data[__lignin_key__]['roles']:
                if existing_entry['name'] == new_active_role:
                    is_existing = True
                    break
            if is_existing:
                cFp_data[__lignin_key__]['active_role'] = new_active_role
                store_updated_cfp_json = True
            else:
                print("[Lignin:ERROR] No role with name {} is defined.".format(new_active_role))
        elif arguments['del-role']:
            del_role = arguments['<name>']
            is_existing = False
            entry_to_delete = None
            for existing_entry in cFp_data[__lignin_key__]['roles']:
                if existing_entry['name'] == del_role:
                    is_existing = True
                    entry_to_delete = existing_entry
                    break
            if is_existing:
                idx_to_del = cFp_data[__lignin_key__]['roles'].index(entry_to_delete)
                del cFp_data[__lignin_key__]['roles'][idx_to_del]
                store_updated_cfp_json = True
            else:
                print("[Lignin:ERROR] No role with name {} is defined.".format(del_role))
    elif arguments['build'] and not arguments['admin']:
        cur_active_role = cFp_data[__lignin_key__]['active_role']
        if arguments['--role'] is not None:
            cur_active_role = arguments['--role']
        if cur_active_role == __none_key__ or cur_active_role == __to_be_defined_key__:
            print("[Lignin:ERROR] A role must be set active first, or defined using the --role option.")
        else:
            is_existing = False
            cur_active_role_dict = None
            for existing_entry in cFp_data[__lignin_key__]['roles']:
                if existing_entry['name'] == cur_active_role:
                    is_existing = True
                    cur_active_role_dict = existing_entry
                    break
            if not is_existing:
                print("[Lignin:ERROR] No role with name {} is defined.".format(cur_active_role))
            else:
                with_debug = False
                with_incr = False
                if arguments['--debug']:
                    with_debug = True
                if arguments['--incr']:
                    with_incr = True
                if arguments['proj']:
                    print("[Lignin:INFO] Starting to create the project files for a monolithic design with role {}..."
                          .format(cur_active_role))
                    # start make and OVERWRITE the environment variables
                    os.system('cd {}; export roleName1={}; export usedRoleDir={}; make monolithic_proj'
                              .format(cfp_root, cur_active_role_dict['name'],
                                      get_cfp_role_path(cfp_root, cur_active_role_dict)))
                elif arguments['monolithic']:
                    info_str = "[Lignin:INFO] Starting to to build a monolithic design with role {}"\
                                .format(cur_active_role)
                    make_cmd = 'monolithic'
                    if with_incr:
                        make_cmd += '_incr'
                        info_str += ' using the incremental build feature'
                    if with_debug:
                        make_cmd += '_debug'
                        info_str += ' and inserting debug probes (as defined in {})'\
                            .format(os.path.abspath(cfp_root + '/TOP/xdc/debug.xdc'))
                    info_str += '...'
                    print(info_str)
                    # start make and OVERWRITE the environment variables
                    os.system('cd {}; export roleName1={}; export usedRoleDir={}; make {}'
                              .format(cfp_root, cur_active_role_dict['name'],
                                      get_cfp_role_path(cfp_root, cur_active_role_dict), make_cmd))
                elif arguments['pr']:
                    if with_incr:
                        print("[Lignin:INFO] Incremental compile with a partial reconfiguration design is not (yet) " +
                          "supported (but anyhow, just the role is build).")
                    info_str = "[Lignin:INFO] Starting to to build a partial reconfiguration design for role {}" \
                        .format(cur_active_role)
                    make_cmd = 'pr2_only'
                    if with_debug:
                        print("[Lignin:ERROR] NOT-YET-IMPLEMENTED (pr build with debug probes).")
                    else:
                        # check for dcp
                        if not os.path.isfile(dcp_file_path) or not os.path.isfile(meta_file_path):
                            # os.system("{} {}/get_latest_dcp.py".format(os.environ['cFsysPy3_cmd'], cfp_env_folder))
                            os.system("{} {}/get_latest_dcp.py".format(cfenv_small_py_bin, cfp_env_folder))
                            if not os.path.isfile(dcp_file_path):
                                print("Lignin:ERROR] No DCP present, can not build pr designs. Stop.")
                                return -1
                    info_str += '...'
                    print(info_str)
                    # start make and OVERWRITE the environment variables
                    os.system('cd {}; export roleName1={}; export usedRoleDir={}; \
                                export roleName2={}; export usedRoleDir2={}; make {}'
                              .format(cfp_root,
                                      # cur_active_role_dict['name'], get_cfp_role_path(cfp_root, cur_active_role_dict),
                                      __to_be_defined_key__, __to_be_defined_key__,  # role 1 should be totally ignored?
                                      cur_active_role_dict['name'], get_cfp_role_path(cfp_root, cur_active_role_dict),
                                      make_cmd))
    elif arguments['admin']:
        if arguments['full_clean']:
            os.system('cd {}; make full_clean'.format(cfp_root))
        elif arguments['set-2nd-role']:
            cFp_data[__lignin_key__][__admin_key__]['2nd-role'] = arguments['<name>']
            store_updated_cfp_json = True
        elif arguments['write-to-json']:
            print("[Lignin:INFO] Writing current role setting to cFp.json.")
            cur_active_role_1 = cFp_data[__lignin_key__]['active_role']
            if cur_active_role_1 == __none_key__ or cur_active_role_1 == __to_be_defined_key__:
                print("[Lignin:ERROR] A role must be set active first, or defined using the --role option.")
            else:
                is_existing = False
                cur_active_role_dict_1 = None
                for existing_entry in cFp_data[__lignin_key__]['roles']:
                    if existing_entry['name'] == cur_active_role_1:
                        is_existing = True
                        cur_active_role_dict_1 = existing_entry
                        break
                if not is_existing:
                    print("[Lignin:ERROR] No role with name {} is defined.".format(cur_active_role_1))
                else:
                    write_2nd_role = True
                    cur_active_role_2 = cFp_data[__lignin_key__][__admin_key__]['2nd-role']
                    cur_active_role_dict_2 = None
                    if cur_active_role_2 == __none_key__ or cur_active_role_2 == __to_be_defined_key__:
                        write_2nd_role = False
                    else:
                        is_existing = False
                        for existing_entry in cFp_data[__lignin_key__]['roles']:
                            if existing_entry['name'] == cur_active_role_2:
                                is_existing = True
                                cur_active_role_dict_2 = existing_entry
                                break
                        if not is_existing:
                            write_2nd_role = False
                        # update cFp struct
                        cFp_data['roleName1'] = cur_active_role_dict_1['name']
                        cFp_data['usedRoleDir'] = cur_active_role_dict_1['path']
                        if write_2nd_role:
                            cFp_data['roleName2'] = cur_active_role_dict_2['name']
                            cFp_data['usedRoleDir2'] = cur_active_role_dict_2['path']
                        store_updated_cfp_json = True
        elif arguments['build']:
            cur_active_role = cFp_data[__lignin_key__]['active_role']
            if cur_active_role == __none_key__ or cur_active_role == __to_be_defined_key__:
                print("[Lignin:ERROR] A role must be set active first, or defined using the --role option.")
            else:
                is_existing = False
                cur_active_role_dict = None
                for existing_entry in cFp_data[__lignin_key__]['roles']:
                    if existing_entry['name'] == cur_active_role:
                        is_existing = True
                        cur_active_role_dict = existing_entry
                        break
                if not is_existing:
                    print("[Lignin:ERROR] No role with name {} is defined.".format(cur_active_role))
                else:
                    if arguments['pr_flash']:
                        # no 2nd role is required
                        info_str = "[Lignin:INFO] Starting to build all files for a new platform logic, using role {}" \
                            .format(cur_active_role)
                        make_cmd = 'pr_flash'
                        info_str += '...'
                        print(info_str)
                        # start make and OVERWRITE the environment variables
                        os.system('cd {}; export roleName1={}; export usedRoleDir={}; \
                                    export roleName2={}; export usedRoleDir2={}; make {}'
                                  .format(cfp_root,
                                           cur_active_role_dict['name'], get_cfp_role_path(cfp_root, cur_active_role_dict),
                                          __to_be_defined_key__, __to_be_defined_key__,  # role 2 should be totally ignored?
                                          # cur_active_role_dict['name'], get_cfp_role_path(cfp_root, cur_active_role_dict),
                                          make_cmd))
                    elif arguments['pr_full']:
                        # two active roles are required
                        cur_active_role_2 = cFp_data[__lignin_key__][__admin_key__]['2nd-role']
                        if cur_active_role_2 == __none_key__ or cur_active_role_2 == __to_be_defined_key__:
                            print("[Lignin:ERROR] A 2nd role must be set active first.")
                        else:
                            is_existing = False
                            cur_active_role_dict_2 = None
                            for existing_entry in cFp_data[__lignin_key__]['roles']:
                                if existing_entry['name'] == cur_active_role_2:
                                    is_existing = True
                                    cur_active_role_dict_2 = existing_entry
                                    break
                            if not is_existing:
                                print("[Lignin:ERROR] No role with name {} is defined.".format(cur_active_role_2))
                            else:
                                info_str = "[Lignin:INFO] Starting to build a *complete* partial reconfiguration design, " + \
                                            "using roles {} and {}" \
                                    .format(cur_active_role, cur_active_role_2)
                                make_cmd = 'pr_full'
                                info_str += '...'
                                print(info_str)
                                # start make and OVERWRITE the environment variables
                                os.system('cd {}; export roleName1={}; export usedRoleDir={}; \
                                            export roleName2={}; export usedRoleDir2={}; make {}'
                                          .format(cfp_root,
                                                  cur_active_role_dict['name'], get_cfp_role_path(cfp_root, cur_active_role_dict),
                                                  cur_active_role_dict_2['name'], get_cfp_role_path(cfp_root, cur_active_role_dict_2),
                                                  make_cmd))

    # finally
    if store_updated_cfp_json:
        # always update version
        cFp_data[__lignin_key__]['version'] = __version__
        with open(cfp_json_file, 'w') as json_file:
            json.dump(cFp_data, json_file, indent=4)
    return


if __name__ == '__main__':
    # vitrualenv is activated by the bash script
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        # This works with virtualenv for Python 3 and 2 and also for the venv module in Python 3
        print("ERROR: It looks like this lignin isn't running in a virtual environment. STOP.")
        sys.exit(1)
    main()
    exit(0)

