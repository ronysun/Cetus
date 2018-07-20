import TestCase.SDK.base as base
import time
import logging

LOG = logging.getLogger("testSuit")
class serversList(base.SDKbase):
    def run(self):
        print self.client.list_images()

class ServerCreate(base.SDKbase):

    def __init__(self):
        super(ServerCreate, self).__init__()
        self.result = None

    def run(self, **kwargs):
        try:
            servers = self.client.create_server(**kwargs)
            self.result = servers['id']
        except:
            LOG.error("run error!")

    def sla(self, **kwargs):
        for loop in range(kwargs.get('wait', 1)):
            time.sleep(1)
            server_status = self.client.get_server(self.result)['vm_state']
            print server_status
            if server_status == kwargs.get('status'):
                LOG.info("case pass")
                return 'p', "case pass", "ironic-13"
        else:
            LOG.info("case failed")
            return 'f', 'case failed', "ironic-13"

    def clean_up(self):
        LOG.info("CLEAN UP in ServerCreate")
        self.client.delete_server(self.result)