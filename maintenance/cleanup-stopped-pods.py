# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@redhat.com>
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
import datetime
import docker


expires = dict(hours=12)

client = docker.Client(base_url='unix://var/run/docker.sock', timeout=10)

containers = client.containers(all=True, filters={'status': 'exited'})

for cont in containers:
    insp = client.inspect_container(cont)
    blah = insp['State']['FinishedAt'].split(".")[0]
    if blah.startswith("00"):  # WTF
        continue
    dt = datetime.datetime.strptime(blah, "%Y-%m-%dT%H:%M:%S")

    if (dt + datetime.timedelta(**expires)) < datetime.datetime.now():
        print(insp['Id'])
