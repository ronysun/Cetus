import TestCase.SDK.base as base
import time
import random
import logging

LOG = logging.getLogger("testSuit")
class serversList(base.SDKbase):
    def run(self):
        print self.client.list_images()

class ServerCreate(base.SDKbase):

    def __init__(self):
        super(ServerCreate, self).__init__()

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
                return 'p', "case pass", "OS-1"
        else:
            LOG.info("case failed")
            return 'f', 'case failed', "OS-1"

    def clean_up(self):
        LOG.info("CLEAN UP in ServerCreate")
        self.client.delete_server(self.result)


class ServerDelete(base.SDKbase):
    def __init__(self):
        super(ServerDelete, self).__init__()
        self.context = None

    def setup(self, **kwargs):
        random_name = "Cetus" + random.randint(0,100)
        name = kwargs.get('name', random_name)
        image = kwargs.get('image', 'ccad6f49-cac3-43b5-8051-0de5dce462c5')
        flavor = kwargs.get('flavor', 'FLAVOR1')
        server = self.client.create_server(name=name, image=image, flavor=flavor)
        for count in range(10):
            server_status = self.client.get_server(server['id'])['vm_state']
            if server_status == "active":
                LOG.info("VM create succeed")
                self.context = server['id']
                return self.context
        else:
            LOG.error("VM create error!")

    def run(self, **kwargs):
        try:
            server = self.setup()
            self.result = self.client.delete_server(server, **kwargs)
        except:
            LOG.error("run error!")

    def sla(self, **kwargs):
        for loop in xrange(kwargs.get('wait', 1)):
            time.sleep(1)
            try:
                self.client.get_server(self.context)
                LOG.error("case failed")
                return 'f', 'case failed', "OS-2"
            except:
                LOG.info("case pass")
                return 'p', "case pass", "OS-2"

    def clean_up(self):
        pass
        LOG.info("clean up context")