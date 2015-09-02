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
import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock', timeout=10)
containers = client.containers(all=True, filters={'status': 'running'})

pods = {}
for cont in containers:

    stats_obj = client.stats(cont)
    rjson = stats_obj.next()
    parsed_json = json.loads(rjson)
    mem_usage = parsed_json['memory_stats']['usage']
    mem_limit = parsed_json['memory_stats']['limit']
    percent   = (mem_usage*100)/mem_limit

    #print mem_usage
    #print mem_limit
    #print percent

    pods[cont['Names'][0]] = {'mem_usage': mem_usage, 'mem_limit': mem_limit, 'percent': percent}


for key, value in sorted(pods.iteritems(), key=lambda kvt: kvt[1]['percent'], reverse=True):
  mem_usage_GB = (value['mem_usage']/1024/1024/1024)
  mem_limit_GB = (value['mem_limit']/1024/1024/1024)
  print ("[%s%%  %s GB/%s GB]  %s") % (value['percent'], mem_usage_GB, mem_limit_GB, key)
