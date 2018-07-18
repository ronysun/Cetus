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
        LOG.info("ServerCrate with: %s" % str(kwargs))
        print "run in ServerCreate"
        servers = self.client.create_server(**kwargs)
        self.result = servers['id']

    def sla(self, **kwargs):
        LOG.info("sla in ServerCreate")
        for loop in range(kwargs.get('wait', 1)):
            time.sleep(1)
            server_status = self.client.get_server(self.result)['vm_state']
            print server_status
            if server_status == kwargs.get('status'):
                LOG.info("case pass")
                return 'p', "case pass", "ironic-13"
        else:
            return 'f', 'case failed'

    def clean_up(self):
        LOG.debug("CLEAN UP in ServerCreate")
        self.client.delete_server(self.result)