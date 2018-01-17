
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

    provides = [OAISPGWServiceInstance]

    observes = OAISPGWServiceInstance

    requested_interval = 0

    template_name = "oaispgwserviceinstance_playbook.yaml"

    service_key_name = "/opt/xos/synchronizers/oaispgw/oaispgw_private_key"

    watches = [ModelLink(ServiceDependency,via='servicedependency'), ModelLink(ServiceMonitoringAgentInfo,via='monitoringagentinfo')]

    def __init__(self, *args, **kwargs):
        super(SyncOAISPGWServiceInstance, self).__init__(*args, **kwargs)

    def get_oaispgw(self, o):
        if not o.owner:
            return None

        oaispgw = OAISPGWService.objects.filter(id=o.owner.id)

        if not oaispgw:
            return None

        return oaispgw[0]

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        fields['tenant_message'] = o.tenant_message
        """
        oaispgw = self.get_oaispgw(o)

        for oai in OAISPGWInstance.objects.all():
            name = oai.tenant_message
            instance = Instance.objects.filter(id=oai.instance_id).first()

            ip = []

            while not ip:
                ip = [port.ip for port in instance.ports.all()]
                time.sleep(2)

            for service, prefix in [('%s_PRIVATE_IP' % name, '10.0'), ('%s_PUBLIC_IP' % name, '10.8')]:
                service_ip = list(filter(lambda x: x.startswith(prefix), ip))[0]
                fields[service] = service_ip
        """

        return fields

    def delete_record(self, port):
        # Nothing needs to be done to delete an exampleservice; it goes away
        # when the instance holding the exampleservice is deleted.
        pass

    def handle_service_monitoringagentinfo_watch_notification(self, monitoring_agent_info):
        if not monitoring_agent_info.service:
            logger.info("handle watch notifications for service monitoring agent info...ignoring because service attribute in monitoring agent info:%s is null" % (monitoring_agent_info))
            return

        if not monitoring_agent_info.target_uri:
            logger.info("handle watch notifications for service monitoring agent info...ignoring because target_uri attribute in monitoring agent info:%s is null" % (monitoring_agent_info))
            return

        objs = OAISPGWServiceInstance.objects.all()
        for obj in objs:
            if obj.owner.id != monitoring_agent_info.service.id:
                logger.info("handle watch notifications for service monitoring agent info...ignoring because service attribute in monitoring agent info:%s is not matching" % (monitoring_agent_info))
                return

            instance = self.get_instance(obj)
            if not instance:
               logger.warn("handle watch notifications for service monitoring agent info...: No valid instance found for object %s" % (str(obj)))
               return

            logger.info("handling watch notification for monitoring agent info:%s for OAISPGWServiceInstance object:%s" % (monitoring_agent_info, obj))

            #Run ansible playbook to update the routing table entries in the instance
            fields = self.get_ansible_fields(instance)
            fields["ansible_tag"] =  obj.__class__.__name__ + "_" + str(obj.id) + "_monitoring"
            fields["target_uri"] = monitoring_agent_info.target_uri

            template_name = "monitoring_agent.yaml"
            super(SyncOAISPGWServiceInstance, self).run_playbook(obj, fields, template_name)
        pass
