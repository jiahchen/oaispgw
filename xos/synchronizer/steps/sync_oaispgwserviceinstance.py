
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import time
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

logger = Logger(level=logging.INFO)

class SyncOAISPGWServiceInstance(SyncInstanceUsingAnsible):

    observes = OAISPGWServiceInstance

    template_name = "oaispgwserviceinstance_playbook.yaml"

    service_key_name = "/opt/xos/synchronizers/oaispgw/oaispgw_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncOAISPGWServiceInstance, self).__init__(*args, **kwargs)

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        #fields['tenant_message'] = o.tenant_message

        return fields

