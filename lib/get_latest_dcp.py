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
#  *     Created: Oct 2021
#  *     Authors: FAB, WEI, NGL, DID
#  *
#  *     Description:
#  *       Python script to download latest dcp file to ./dcps/
#  *

import os
import json
import requests

__cfp_json_path__ = "/../cFp.json"
__shell_type_key__ = 'cFpSRAtype'
__mod_type_key__ = 'cFpMOD'
__dcps_folder_name__ = '/dcps/'

__credentials_file_name__ = "user.json"

__openstack_user_template__ = {'credentials': {'user': "your user name", 'pw': "your user password"},
                               'project': "default"}

__cf_manager_url__ = "10.12.0.132:8080"


def load_user_credentials(filedir):
    json_file = filedir + "/" + __credentials_file_name__
    global __openstack_user__
    global __openstack_pw__
    global __openstack_project__

    try:
        with open(json_file, 'r') as infile:
            data = json.load(infile)
        __openstack_user__ = data['credentials']['user']
        __openstack_pw__ = data['credentials']['pw']
        if 'project' in data:
            __openstack_project__ = data['project']
        return 0
    except Exception as e:
        print(e)
        print("Writing credentials template to {}\n".format(json_file))

    with open(json_file, 'w') as outfile:
        json.dump(__openstack_user_template__, outfile)
    return -1


def main():
    me_abs = os.path.dirname(os.path.realpath(__file__))
    cfp_json_file = me_abs + __cfp_json_path__
    debugging_flow = os.environ.get('CFP_DEBUGGING')
    if debugging_flow is not None:
        cfp_json_file = me_abs + '/../../cFp/cFp_Triangle/cFp.json'
    with open(cfp_json_file, 'r') as json_file:
        cFp_data = json.load(json_file)

    root_abs = os.path.realpath(me_abs+"/../")
    if debugging_flow is not None:
        root_abs = os.path.realpath(me_abs + "/../../cFp/cFp_Triangle/env/" + "/../")
    cFp_data['abs_path'] = root_abs

    shell_type = cFp_data[__shell_type_key__]

    if load_user_credentials(root_abs) == -1:
        print("Please save your (escaped) OpenStack credentials in {}/{}".format(root_abs, __credentials_file_name__))
        exit(1)

    cfrm_url = __cf_manager_url__
    if debugging_flow is not None:
        cfrm_url = "localhost:8080"

    requests_error = False
    try:
        r1 = requests.get("http://"+cfrm_url+"/composablelogic/by_shell/"+str(shell_type)
                          +"?username={0}&password={1}".format(__openstack_user__, __openstack_pw__))
    except Exception as e:
        print(str(e))
        requests_error = True

    if requests_error or r1.status_code != 200:
        print("ERROR: Failed to connect to CFRM ({}). STOP.".format(r1.status_code))
        exit(1)

    r1_list = json.loads(r1.text)
    latest_shell_id = r1_list[-1]['id']

    dcps_folder = root_abs + __dcps_folder_name__
    os.system("mkdir -p {}".format(dcps_folder))
    dcp_file_name = "3_top{}_STATIC.dcp".format(cFp_data[__mod_type_key__])
    target_file_name = os.path.abspath(dcps_folder + "/" + dcp_file_name)
    download_url = "http://"+cfrm_url+"/composablelogic/"+str(latest_shell_id)+"/dcp" + \
                   "?username={0}&password={1}".format(__openstack_user__, __openstack_pw__)
    err_msg = ""
    with requests.get(download_url, stream=True) as r2:
        r2.raise_for_status()
        if r2.status_code != 200:
            requests_error = True
            err_msg = "{}".format(r2.status_code)
        with open(target_file_name, 'wb') as f:
            for chunk in r2.iter_content(chunk_size=8192):
                f.write(chunk)

    if requests_error:
        print("ERROR: Failed to download latest dcp ({}). STOP.".format(err_msg))
        exit(1)

    print("[cFBuild] Updated dcp of Shell '{}' to latest version ({}) successfully.\n\t(downloaded dcp to {})"
          .format(shell_type, latest_shell_id, target_file_name))


if __name__ == '__main__':
    main()
    exit(0)

