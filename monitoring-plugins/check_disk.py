#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Florian Lambert <flambert@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Requirments: python
#

import sys
import argparse
import subprocess

VERSION = '1.0'

STATE_TEXT = ['Ok', 'Warning', 'Critical', 'Unknow']


PARSER = argparse.ArgumentParser(description='Disk check recurcive')
PARSER.add_argument("-b", "--base",
                    type=str,
                    help='base directory to monitor. For example if you want to monitor only volume mounted under /host/ (Default: /)',
                    default="/")
PARSER.add_argument("-e", "--excludes",
                    type=str, nargs='+',
                    help='List of mountpoint to recurcively exclude ex: /var/lib/origin /var/lib/docker',
                    default=[])
PARSER.add_argument("-w", "--warning",
                    type=int,
                    help='Warning value (Default: 85)',
                    default=85)
PARSER.add_argument("-c", "--critical",
                    type=int,
                    help='Critical value (Default: 95)',
                    default=95)
PARSER.add_argument("-v", "--version",
                    action='store_true',
                    help='Print script version')
ARGS = PARSER.parse_args()



def check_df(base,warning,critical,excludes):
    STATE_OK = 0
    STATE_WARNING = 1
    STATE_CRITICAL = 2
    STATE_UNKNOWN = 3
    STATE = STATE_OK

    df_cmd = ("df --exclude-type=tmpfs "
              "--exclude-type=devtmpfs "
              "--output=source,target,fstype,iused,itotal,ipcent,used,size,pcent "
              "--block-size G")

    stdout = subprocess.check_output(df_cmd, shell=True).strip().split("\n")
    # remove the header output
    del stdout[0]

    _output_message = []
    _disk_ok = []
    for line in stdout:
        # Exclude filter on target mount point
        col = line.split()
        # 0: source
        # 1: target
        # 2: fstype
        # 3: iused
        # 4: itotal
        # 5: ipcent
        # 6: used
        # 7: size
        # 8: pcent
        if is_excluded(excludes,col[1]):
            continue
        if not is_based(base,col[1]):
            continue
        _disk_ok.append(col[1])

        # csize: pourcent usage
        csize = int(col[8].rstrip('%'))
        if csize >= int(critical):  # CRITICAL
            STATE = STATE_CRITICAL
            _output_message.append("Disk Block %s %s Used" % (col[1], col[8]))
        elif csize >= int(warning):  # WARNING
            # Update state warning only if the current is not critical
            if STATE < STATE_CRITICAL:
                STATE = STATE_WARNING
            _output_message.append("Disk Block %s %s Used" % (col[1], col[8]))

        # cinode: pourcent usage inode
        cinode = int(col[5].rstrip('%'))
        if cinode >= int(critical):  # CRITICAL
            STATE = STATE_CRITICAL
            _output_message.append("Disk Inode %s %s Used" % (col[1], col[5]))
        elif cinode >= int(warning):  # WARNING
            # Update state warning only if the current is not critical
            if STATE < STATE_CRITICAL:
                STATE = STATE_WARNING
            _output_message.append("Disk Inode %s %s Used" % (col[1], col[5]))

    if STATE == STATE_OK:
        output_message = "Disk %s" % (' || '.join(_disk_ok))
    else:
        output_message = ' || '.join(_output_message)
    return output_message,STATE

def is_excluded(excludes,path):
    #Check if the mount path is in the excludes
    for ex in excludes:
        if path.startswith(ex):
            return True
    return False

def is_based(base,path):
    #Check if the mount path is in the base path
    if path.startswith(base):
        return True
    return False

if __name__ == "__main__":

    if ARGS.version:
        print "version: %s" % (VERSION)
        sys.exit(0)

    (OUTPUT_MESSAGE,STATE) = check_df(base=ARGS.base,
                                      warning=ARGS.warning,
                                      critical=ARGS.critical,
                                      excludes=ARGS.excludes)

    try:
        print "%s: %s" % (STATE_TEXT[STATE], OUTPUT_MESSAGE)
        sys.exit(STATE)
    except ValueError:
        print "Oops!  cant return STATE"
