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
#  *       Python script to create build signature file for new platform logics
#  *

import sys
import os
import json
import hashlib

# 'hardcoded' version strings
# __THIS_FILE_VERSION_NUMBER__ = 3
# __THIS_FILE_VERSION_STRING__ = "0.0.3"
__THIS_FILE_ALGORITHM_VERSION = 'hc1'  # hash concat version 1

__cfp_json_path__ = '/../cFp.json'
__shell_type_key__ = 'cFpSRAtype'
__mod_type_key__ = 'cFpMOD'
__dcps_folder_name__ = '/dcps/'
__sig_file_ending__ = 'sig'
__admin_sig_file_name__ = 'admin'


def get_file_hash(file_path):
    # # check right version
    # assert __THIS_FILE_ALGORITHM_VERSION == 'hc1'
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_string_hash(inp_string):
    # # check right version
    # assert __THIS_FILE_ALGORITHM_VERSION == 'hc1'
    sha256_hash = hashlib.sha256(inp_string.encode('utf-8'))
    return sha256_hash.hexdigest()


def get_admin_sig_string(dcp_hash, mcs_hash, bit_hash, rpt_hash, debugging_flow=None):
    # # check right version
    # assert __THIS_FILE_ALGORITHM_VERSION == 'hc1'
    new_cert_string = 'new_pl:' + str(dcp_hash) + str(mcs_hash) + str(bit_hash) + str(rpt_hash)
    cert = hashlib.sha384(new_cert_string.encode('utf-8')).hexdigest()
    if debugging_flow is not None:
        print("\tnew_cert_string: {}".format(new_cert_string))
    return cert


def main(new_mcs_file_name, new_bit_file_name, pr_verify_rpt_file_name):
    # we print only on error
    me_abs_dir = os.path.dirname(os.path.realpath(__file__))
    me_abs_file = os.path.abspath(os.path.realpath(__file__))
    cfp_json_file = me_abs_dir + __cfp_json_path__
    debugging_flow = os.environ.get('CFP_DEBUGGING')
    if debugging_flow is not None:
        cfp_json_file = me_abs_dir + debugging_flow + '/cFp.json'
    with open(cfp_json_file, 'r') as json_file:
        cFp_data = json.load(json_file)

    # 1. check folders and file names
    root_abs = os.path.realpath(me_abs_dir+"/../")
    if debugging_flow is not None:
        root_abs = os.path.realpath(me_abs_dir + debugging_flow + "/env/" + "/../")
    cFp_data['abs_path'] = root_abs
    dcps_folder = root_abs + __dcps_folder_name__
    # folder should exist...
    dcp_file_name = "3_top{}_STATIC.dcp".format(cFp_data[__mod_type_key__])
    target_file_name = os.path.abspath(dcps_folder + "/" + dcp_file_name)
    # meta_file_name = "3_top{}_STATIC.json".format(cFp_data[__mod_type_key__])
    # target_meta_name = os.path.abspath(dcps_folder + "/" + meta_file_name)

    new_mcs_file_path = os.path.abspath(dcps_folder + '/' + new_mcs_file_name)
    if not os.path.isfile(new_mcs_file_path):
        print("[cFBuild] ERROR: {} is not a file. STOP.".format(new_mcs_file_path))
        exit(1)

    new_bit_file_path = os.path.abspath(dcps_folder + '/' + new_bit_file_name)
    if not os.path.isfile(new_bit_file_path):
        print("[cFBuild] ERROR: {} is not a file. STOP.".format(new_bit_file_path))
        exit(1)

    pr_verify_rpt_file_path = os.path.abspath(dcps_folder + '/' + pr_verify_rpt_file_name)
    if not os.path.isfile(pr_verify_rpt_file_path):
        print("[cFBuild] ERROR: {} is not a file. STOP.".format(pr_verify_rpt_file_path))
        exit(1)
    rpt_file_lines = []
    with open(pr_verify_rpt_file_path) as rpt_in:
        for line in rpt_in:
            rpt_file_lines.append(line.rstrip())
    pr_verify_str = ''.join(rpt_file_lines)

    sig_file_path = os.path.abspath(dcps_folder + '/' + __admin_sig_file_name__ + '.' + __sig_file_ending__)
    # to have all the expected keys
    new_sig = {'build_id': __admin_sig_file_name__, 'algorithm': __admin_sig_file_name__,
               'file': __admin_sig_file_name__, 'pl_id': 'new_pl', 'hash': 'ignore'}

    # with open(target_meta_name, 'r') as meta_file:
    #     cur_meta = json.load(meta_file)
    # current_cl_cert = cur_meta['cert']
    # pl_id = cur_meta['id']
    # for Mantles
    # if 'pl_id' in cur_meta:
    #     pl_id = cur_meta['pl_id']
    # new_sig['pl_id'] = pl_id

    # crete new cert
    dcp_hash = get_file_hash(target_file_name)
    # my_hash = get_file_hash(me_abs_file)
    mcs_hash = get_file_hash(new_mcs_file_path)
    bit_hash = get_file_hash(new_bit_file_path)
    # rpt_hash = get_file_hash(pr_verify_rpt_file_path) # not file!
    rpt_hash = get_string_hash(pr_verify_str)

    if debugging_flow is not None:
        print("\tdcp hash: {}".format(dcp_hash))
        print("\trpt hash: {}".format(rpt_hash))
        print("\tbit hash: {}".format(bit_hash))
        print("\tmcs hash: {}".format(mcs_hash))
        # print("\tmy hash: {}".format(my_hash))

    new_sig['sig'] = get_admin_sig_string(dcp_hash, mcs_hash, bit_hash, rpt_hash, debugging_flow=debugging_flow)
    new_sig['dcp_hash'] = dcp_hash  # to check for transport errors first?
    new_sig['mcs_hash'] = mcs_hash
    new_sig['bit_hash'] = bit_hash
    new_sig['rpt_hash'] = rpt_hash

    rpt_sum_line = rpt_file_lines[-1]
    new_sig['verify_rpt'] = rpt_sum_line
    if dcp_file_name in rpt_sum_line:
        new_sig['verify'] = 'OK'
    else:
        new_sig['verify'] = 'NOK'

    with open(sig_file_path, 'w') as outfile:
        json.dump(new_sig, outfile)

    return 0


if __name__ == '__main__':
    # we print only on error
    if len(sys.argv) != 4:
        print('ERROR: Usage is {} <new-mcs-file-name> <new-bit-file-name> <pr-verify-rpt-file-name>. STOP'
              .format(sys.argv[0]))
        exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
    exit(0)

