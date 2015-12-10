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
# Pods : Allow you to check if pods registry and router are running.
# Nodes : Check if nodes status isn't Running

import sys
import argparse
import subprocess
import requests

# Disable warning for insecure https
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

VERSION = '1.1'

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

STATE_TEXT = ['Ok', 'Warning', 'Critical', 'Unknow']

STATE = STATE_OK
OUTPUT_MESSAGE = ''

PARSER = argparse.ArgumentParser(description='Openshift check pods')
PARSER.add_argument("-proto", "--protocol", type=str,
                    help='Protocol openshift (Default : https)',
                    default="https")
PARSER.add_argument("-api", "--base_api", type=str,
                    help='Url api and version (Default : /api/v1/)',
                    default="/api/v1/")
PARSER.add_argument("-H", "--host", type=str,
                    help='Host openshift (Default : 127.0.0.1)',
                    default="127.0.0.1")
PARSER.add_argument("-P", "--port", type=str,
                    help='Port openshift (Default : 8443)',
                    default=8443)
PARSER.add_argument("-u", "--username", type=str,
                    help='Username openshift (ex : sensu)')
PARSER.add_argument("-p", "--password", type=str,
                    help='Password openshift')
PARSER.add_argument("-to", "--token", type=str,
                    help='File with token openshift (like -t)')
PARSER.add_argument("-tf", "--tokenfile", type=str,
                    help='Token openshift (use token or user/pass')
PARSER.add_argument("--check_nodes", action='store_true',
                    help='Check status of all nodes')
PARSER.add_argument("--check_pods", action='store_true',
                    help='Check status of pods ose-haproxy-router and ose-docker-registry')
PARSER.add_argument("--check_scheduling", action='store_true',
                    help='Check if your nodes is in SchedulingDisabled stat. Only warning')
PARSER.add_argument("--check_labels", action='store_true',
                    help='Check if your nodes have your "OFFLINE" label. Only warning (define by --label_offline)')
PARSER.add_argument("--label_offline", type=str,
                    help='Your "OFFLINE" label name (Default: retiring)',
                    default="retiring")
PARSER.add_argument("-v", "--version", action='store_true',
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
               base_api='/api/v1/'):

     self.os_STATE = 0
     self.os_OUTPUT_MESSAGE = ''

     self.proto     = proto
     self.host      = host
     self.port      = port
     self.username  = username
     self.password  = password
     self.debug     = debug
     self.verbose   = verbose
     self.namespace = namespace
     self.base_api  = base_api

     if token:
         self.token = token
     elif tokenfile:
         self.token=self._tokenfile(tokenfile)
     else:
         self.token=self._auth()

  def _auth(self):
     cmd="oc login %s:%s -u%s -p%s --insecure-skip-tls-verify=True 2>&1 > /dev/null" % (self.host, self.port, self.username, self.password)
     subprocess.check_output(cmd, shell=True)

     cmd="oc whoami -t"
     stdout = subprocess.check_output(cmd, shell=True)

     return stdout.strip()

  def _tokenfile(self,tokenfile):
     try:
       f = open(tokenfile, 'r')
       return f.readline().strip()
     except IOError:
       self.os_OUTPUT_MESSAGE += ' Error: File does not appear to exist'
       self.os_STATE = 2
       return "tokenfile-inaccessible"

  def get_scheduling(self):

     self.os_OUTPUT_MESSAGE += ' Nodes: '

     api_nodes = self.base_api + 'nodes'
     headers = {"Authorization": 'Bearer %s' % self.token}
     r = requests.get('https://%s:%s%s' % (self.host, self.port, api_nodes),
                       headers=headers,
                       verify=False) # don't check ssl
     try:
       parsed_json = r.json()
     except ValueError:
       print "%s: GET %s %s" % (STATE_TEXT[STATE_UNKNOWN],api_nodes , r.text[:200])
       sys.exit(STATE_UNKNOWN)

     # Return unknow if we can't find datas
     if not 'items' in parsed_json:
         self.os_STATE = STATE_UNKNOWN
         self.os_OUTPUT_MESSAGE = ' Unable to find nodes data in the response.'
         return

     all_nodes_names=''
     for item in parsed_json["items"]:
       all_nodes_names += '%s ' % item["metadata"]["name"]

       #print item["metadata"]["name"]
       #print item["status"]["addresses"][0]["address"]
       #print item["status"]["conditions"][0]["type"]
       #print item["status"]["conditions"][0]["status"]
       #print item["status"]["conditions"][0]["reason"]

       try:
         if item["spec"]["unschedulable"]:
           self.os_STATE = 1
           schedule_flag = True
           self.os_OUTPUT_MESSAGE += "%s/%s: [SchedulingDisabled] " % (item["metadata"]["name"],
                                                                       item["status"]["addresses"][0]["address"])
       except:
         schedule_flag = False

     if self.os_STATE == 0:
        self.os_OUTPUT_MESSAGE += "%s [Schedulable]" % (all_nodes_names)

  def get_nodes(self):

     self.os_OUTPUT_MESSAGE += ' Nodes: '

     api_nodes = self.base_api + 'nodes'
     headers = {"Authorization": 'Bearer %s' % self.token}
     r = requests.get('https://%s:%s%s' % (self.host, self.port, api_nodes),
                       headers=headers,
                       verify=False) # don't check ssl
     try:
       parsed_json = r.json()
     except ValueError:
       print "%s: GET %s %s" % (STATE_TEXT[STATE_UNKNOWN],api_nodes , r.text[:200])
       sys.exit(STATE_UNKNOWN)

     # Return unknow if we can't find datas
     if not 'items' in parsed_json:
         self.os_STATE = STATE_UNKNOWN
         self.os_OUTPUT_MESSAGE = ' Unable to find nodes data in the response.'
         return

     # Return unknow if we can't find datas
     if not 'items' in parsed_json:
         self.os_STATE = STATE_UNKNOWN
         self.os_OUTPUT_MESSAGE = ' Unable to find nodes data in the response.'
         return

     all_nodes_names=''
     for item in parsed_json["items"]:
       all_nodes_names += '%s ' % item["metadata"]["name"]

       #print item["metadata"]["name"]
       #print item["status"]["addresses"][0]["address"]
       #print item["status"]["conditions"][0]["type"]
       #print item["status"]["conditions"][0]["status"]
       #print item["status"]["conditions"][0]["reason"]

       #if status not ready
       if item["status"]["conditions"][0]["status"] != "True":
          self.os_STATE = 2
          self.os_OUTPUT_MESSAGE += "%s/%s: [%s %s] " % (item["metadata"]["name"],
                                                         item["status"]["addresses"][0]["address"],
                                                         item["status"]["conditions"][0]["status"],
                                                         item["status"]["conditions"][0]["reason"])

     if self.os_STATE == 0:
        self.os_OUTPUT_MESSAGE += "%s [Ready]" % (all_nodes_names)

  def get_pods(self,namespace=None):

     self.os_OUTPUT_MESSAGE += ' Pods: '

     if namespace:
         self.namespace = namespace
     api_pods = '%snamespaces/%s/pods' % (self.base_api, self.namespace)

     headers = {"Authorization": 'Bearer %s' % self.token}
     r = requests.get('https://%s:%s%s' % (self.host, self.port, api_pods),
                       headers=headers,
                       verify=False) # don't check ssl
     try:
       parsed_json = r.json()
     except ValueError:
       print "%s: GET %s %s" % (STATE_TEXT[STATE_UNKNOWN], api_pods, r.text[:200])
       sys.exit(STATE_UNKNOWN)

     pods = {}

     if self.base_api == '/api/v1beta3/':
        status_condition = 'Condition'
     else:
        status_condition = 'conditions'

     # Return unknow if we can't find datas
     if not 'items' in parsed_json:
         self.os_STATE = STATE_UNKNOWN
         self.os_OUTPUT_MESSAGE = ' Unable to find nodes data in the response.'
         return

     for item in parsed_json["items"]:
       #print item["metadata"]["name"]
       #print item["metadata"]["labels"]["deploymentconfig"]
       #print item["status"]["phase"]
       #print item["status"][status_condition][0]["type"]
       #print item["status"][status_condition][0]["status"]
       try:
         if item["status"][status_condition][0]["status"] != "True":
            if 'deploymentconfig' in item["metadata"]["labels"].keys():
              pods[item["metadata"]["labels"]["deploymentconfig"]] = "%s: [%s] " % (item["metadata"]["name"],
                                                                                    item["status"]["phase"],
                                                                                    item["status"][status_condition][0]["status"])
              self.os_STATE = 2
         else:
            if 'deploymentconfig' in item["metadata"]["labels"].keys():
              pods[item["metadata"]["labels"]["deploymentconfig"]] = "%s: [%s] " % (item["metadata"]["name"],
                                                                                    item["status"]["phase"])
       except:
         pass

     registry_dc_name = 'docker-registry'
     router_dc_name = 'router'

     if registry_dc_name in pods:
        self.os_OUTPUT_MESSAGE += pods[registry_dc_name]
     else:
        self.os_OUTPUT_MESSAGE += '%s [Missing] ' % registry_dc_name
        self.os_STATE = 2

     if router_dc_name in pods:
        self.os_OUTPUT_MESSAGE += pods[router_dc_name]
     else:
        self.os_OUTPUT_MESSAGE += '%s [Missing] ' % router_dc_name
        self.os_STATE = 2


  def get_labels(self,label_offline):

     self.os_OUTPUT_MESSAGE += ' Nodes: '

     api_nodes = self.base_api + 'nodes'
     headers = {"Authorization": 'Bearer %s' % self.token}
     r = requests.get('https://%s:%s%s' % (self.host, self.port, api_nodes),
                       headers=headers,
                       verify=False) # don't check ssl
     try:
       parsed_json = r.json()
     except ValueError:
       print "%s: GET %s %s" % (STATE_TEXT[STATE_UNKNOWN],api_nodes , r.text[:200])
       sys.exit(STATE_UNKNOWN)

     # Return unknow if we can't find datas
     if not 'items' in parsed_json:
         self.os_STATE = STATE_UNKNOWN
         self.os_OUTPUT_MESSAGE = ' Unable to find nodes data in the response.'
         return

     all_nodes_names=''
     for item in parsed_json["items"]:
       all_nodes_names += '%s ' % item["metadata"]["name"]

       #print item["metadata"]["labels"]["region"]
       #print item["status"]["addresses"][0]["address"]
       #print item["status"]["conditions"][0]["type"]
       #print item["status"]["conditions"][0]["status"]
       #print item["status"]["conditions"][0]["reason"]
       #if status not ready
       if label_offline in item["metadata"]["labels"].keys():
          self.os_STATE = 1 #just warning
          self.os_OUTPUT_MESSAGE += "%s/%s: [Label: %s] " % (item["metadata"]["name"],
                                                             item["status"]["addresses"][0]["address"],
                                                             label_offline)

     if self.os_STATE == 0:
        self.os_OUTPUT_MESSAGE += '%s[schedulable]' % all_nodes_names


if __name__ == "__main__":

   # https://docs.openshift.com/enterprise/3.0/rest_api/openshift_v1.html

   if ARGS.version:
      print "version: %s" % (VERSION)
      sys.exit(0)

   if ARGS.token:
      myos = Openshift(host=ARGS.host,
                       port=ARGS.port,
                       token=ARGS.token,
                       proto=ARGS.protocol,
                       base_api=ARGS.base_api)
   elif ARGS.tokenfile:
      myos = Openshift(host=ARGS.host,
                       port=ARGS.port,
                       tokenfile=ARGS.tokenfile,
                       proto=ARGS.protocol,
                       base_api=ARGS.base_api)
   elif ARGS.username and ARGS.password:
      myos = Openshift(host=ARGS.host,
                       port=ARGS.port,
                       username=ARGS.username,
                       password=ARGS.password,
                       proto=ARGS.protocol,
                       base_api=ARGS.base_api)
   else:
      PARSER.print_help()
      sys.exit(STATE_UNKNOWN)

   if ARGS.check_nodes:
      myos.get_nodes()

   if ARGS.check_pods:
      myos.get_pods()

   if ARGS.check_labels:
      myos.get_labels(ARGS.label_offline)

   if ARGS.check_scheduling:
      myos.get_scheduling()

   try:
     STATE = myos.os_STATE
     OUTPUT_MESSAGE = myos.os_OUTPUT_MESSAGE

     print "%s:%s" % (STATE_TEXT[STATE], OUTPUT_MESSAGE)
     sys.exit(STATE)
   except ValueError:
     print "Oops!  cant return STATE"
