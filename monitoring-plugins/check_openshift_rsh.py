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
import requests

# Disable warning for insecure https
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from requests.exceptions import ConnectionError

VERSION = '1.1'

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

STATE_TEXT = ['Ok', 'Warning', 'Critical', 'Unknow']

STATE = STATE_OK
OUTPUT_MESSAGE = ''

PARSER = argparse.ArgumentParser(description='Openshift check pods')
PARSER.add_argument("-proto", "--protocol",
                    type=str,
                    help='Protocol openshift (Default : https)',
                    choices=['http', 'https'],
                    default="https")
PARSER.add_argument("-api", "--base_api",
                    type=str,
                    help='Url api and version (Default : /api/v1)',
                    default="/api/v1")
PARSER.add_argument("-H", "--host",
                    type=str,
                    help='Host openshift (Default : 127.0.0.1)',
                    default="127.0.0.1")
PARSER.add_argument("-P", "--port",
                    type=int,
                    help='Port openshift (Default : 8443)',
                    default=8443)
PARSER.add_argument("-pn", "--podname",
                    type=str,
                    help='begining of the pods name')
PARSER.add_argument("-n", "--namespace",
                    type=str,
                    help="Namespace",
                    default="default")
PARSER.add_argument("-w", "--warning",
                    type=int,
                    help='Warning value (Default : 85)',
                    default=85)
PARSER.add_argument("-c", "--critical",
                    type=int,
                    help='Critical value (Default : 95)',
                    default=95)
PARSER.add_argument("-u", "--username",
                    type=str,
                    help='Username openshift (ex : sensu)')
PARSER.add_argument("-p", "--password",
                    type=str,
                    help='Password openshift')
PARSER.add_argument("-to", "--token",
                    type=str,
                    help='File with token openshift (like -t)')
PARSER.add_argument("-tf", "--tokenfile",
                    type=str,
                    help='Token openshift (use token or user/pass')
PARSER.add_argument("--check_df",
                    action='store_true',
                    help='Check disk usage in the pod')
PARSER.add_argument("-v", "--version",
                    action='store_true',
                    help='Print script version')
ARGS = PARSER.parse_args()


class Openshift(object):
    """
    A little object for use REST openshift v3 api
    """

    def __init__(self,
                 proto='https',
                 host='127.0.0.1',
                 port=8443,
                 username=None,
                 password=None,
                 token=None,
                 tokenfile=None,
                 debug=False,
                 verbose=False,
                 namespace='default',
                 base_api='/api/v1'):

        self.os_STATE = 0
        self.os_OUTPUT_MESSAGE = ''

        self.proto = proto
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.debug = debug
        self.verbose = verbose
        self.namespace = namespace
        # Remove the trailing / to avoid user issue
        self.base_api = base_api.rstrip('/')

        if token:
            self.token = token
        elif tokenfile:
            self.token = self._tokenfile(tokenfile)
        else:
            self.token = self._auth()

    def _auth(self):
        cmd = ("oc login %s:%s -u%s -p%s --insecure-skip-tls-verify=True 2>&1 > /dev/null"
               % (self.host, self.port, self.username, self.password))
        subprocess.check_output(cmd, shell=True)

        cmd = "oc whoami -t"
        stdout = subprocess.check_output(cmd, shell=True)

        return stdout.strip()

    def _tokenfile(self, tokenfile):
        try:
            f = open(tokenfile, 'r')
            return f.readline().strip()
        except IOError:
            self.os_OUTPUT_MESSAGE += ' Error: File does not appear to exist'
            self.os_STATE = 2
            return "tokenfile-inaccessible"

    def get_json(self, url):

        headers = {"Authorization": 'Bearer %s' % self.token}
        try:
            r = requests.get('https://%s:%s%s' % (self.host, self.port, url),
                             headers=headers,
                             verify=False)  # don't check ssl
            parsed_json = r.json()
        except ValueError:
            print "%s: GET %s %s" % (STATE_TEXT[STATE_UNKNOWN], url, r.text[:200])
            sys.exit(STATE_UNKNOWN)
        except ConnectionError as e:
            print "https://%s:%s%s - %s" % (self.host, self.port, url, e)
            sys.exit(STATE_CRITICAL)

        return parsed_json


    def check_df(self, pod):

        exclude_mount = ['/etc/hosts']
        df_cmd = ("df --exclude-type=tmpfs "
                  "--exclude-type=devtmpfs "
                  "--output=source,target,fstype,iused,itotal,ipcent,used,size,pcent "
                  "--block-size G")
        cmd = ("oc -n %s rsh %s %s 2>&1"
               % (self.namespace, pod, df_cmd))

        stdout = subprocess.check_output(cmd, shell=True).strip().split("\n")
        # remove the header output
        del stdout[0]

        _output_message = []
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
            if col[1] in exclude_mount:
                continue

            # csize: pourcent usage
            csize = int(col[8].rstrip('%'))
            if csize >= int(self.critical):  # CRITICAL
                self.os_STATE = STATE_CRITICAL
                _output_message.append("Disk Block %s: %s %s Used" % (pod, col[1], col[8]))
            elif csize >= int(self.warning):  # WARNING
                # Update state warning only if the current is not critical
                if self.os_STATE < STATE_CRITICAL:
                    self.os_STATE = STATE_WARNING
                _output_message.append("Disk Block %s: %s %s Used" % (pod, col[1], col[8]))

            # cinode: pourcent usage inode
            cinode = int(col[5].rstrip('%'))
            if self.os_STATE < STATE_CRITICAL:  # CRITICAL
                self.os_STATE = STATE_WARNING
                _output_message.append("Disk Inode %s: %s %s Used" % (pod, col[1], col[5]))
            elif cinode >= int(self.warning):  # WARNING
                # Update state warning only if the current is not critical
                if cinode >= int(self.critical):
                    self.os_STATE = STATE_CRITICAL
                _output_message.append("Disk Inode %s: %s %s Used" % (pod, col[1], col[5]))

        self.os_OUTPUT_MESSAGE += ' || '.join(_output_message)

    def start_processing(self, podname=None, namespace=None, check=None, warning=85, critical=95):

        self.namespace = namespace or self.namespace
        self.warning = warning
        self.critical = critical

        api_pods = '%s/namespaces/%s/pods' % (self.base_api, self.namespace)

        parsed_json = self.get_json(api_pods)

        # Return unknow if we can't find datas
        if 'items' not in parsed_json:
            self.os_STATE = STATE_UNKNOWN
            self.os_OUTPUT_MESSAGE = ' Unable to find nodes data in the response.'
            return

        pods = []
        for item in parsed_json["items"]:

            if item["metadata"]["name"].startswith(podname):
                pods.append(item["metadata"]["name"])
                if check == "check_df":
                    self.check_df(item["metadata"]["name"])

        if not pods:
            self.os_OUTPUT_MESSAGE += '%s [Missing] ' % podname
            self.os_STATE = STATE_CRITICAL

        if self.os_STATE == STATE_OK:
            self.os_OUTPUT_MESSAGE = ' Block/Inode %s' % (', '.join(pods))


if __name__ == "__main__":

    # https://docs.openshift.com/enterprise/3.0/rest_api/openshift_v1.html

    if ARGS.version:
        print "version: %s" % (VERSION)
        sys.exit(0)

    if not ARGS.token and not ARGS.tokenfile and not (ARGS.username and ARGS.password):
        PARSER.print_help()
        sys.exit(STATE_UNKNOWN)

    myos = Openshift(host=ARGS.host,
                     port=ARGS.port,
                     username=ARGS.username,
                     password=ARGS.password,
                     token=ARGS.token,
                     tokenfile=ARGS.tokenfile,
                     proto=ARGS.protocol,
                     namespace=ARGS.namespace,
                     base_api=ARGS.base_api)

    if ARGS.check_df:
        myos.start_processing(podname=ARGS.podname,
                              check="check_df",
                              warning=ARGS.warning,
                              critical=ARGS.critical)

    try:
        STATE = myos.os_STATE
        OUTPUT_MESSAGE = myos.os_OUTPUT_MESSAGE

        print "%s:%s" % (STATE_TEXT[STATE], OUTPUT_MESSAGE)
        sys.exit(STATE)
    except ValueError:
        print "Oops!  cant return STATE"
