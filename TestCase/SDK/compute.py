import time
import random
import logging
import common.taf_log as taf_log
import TestCase.SDK.utils as SDK

LOG = logging.getLogger("testlog")


class ServerCreate(SDK.SDKbase):

    def __init__(self):
        super(ServerCreate, self).__init__()

    @taf_log.debug_log
    def run(self, **kwargs):
        try:
            servers = self.client.create_server(**kwargs)
            self.result = servers['id']
        except:
            LOG.error("run error!")

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-1")
    def sla(self, **kwargs):
        for loop in range(kwargs.get('wait', 1)):
            time.sleep(1)
            server_status = self.client.get_server(self.result)['vm_state']
            if server_status == kwargs.get('status'):
                LOG.info("case pass")
                return 'p', 'case pass'
        else:
            LOG.info("case failed")
            return 'f', 'case failed'

    def teardown(self):
        LOG.info("teardown in ServerCreate")
        self.client.delete_server(self.result)


class ServerDelete(SDK.SDKbase):
    def __init__(self):
        super(ServerDelete, self).__init__()
        self.context = None

    def setup(self, **kwargs):
        random_name = "Cetus" + str(random.randint(0, 100))
        name = kwargs.get('name', random_name)
        image = kwargs.get('image', 'ccad6f49-cac3-43b5-8051-0de5dce462c5')
        flavor = kwargs.get('flavor', 'FLAVOR1')
        server = self.client.create_server(name=name, image=image, flavor=flavor)
        for count in range(10):
            server_status = self.client.get_server(server['id'])['vm_state']
            if server_status == "active":
                LOG.info("VM create succeed, named: %s" % name)
                self.context = server['id']
                return self.context
        else:
            LOG.error("VM create error, named: %s" % name)

    @taf_log.debug_log
    def run(self, **kwargs):
        result = self.client.delete_server(self.context, **kwargs)
        if result:
            LOG.info('VM delete')
        else:
            LOG.error('VM not exist!')

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-2")
    def sla(self, **kwargs):
        for loop in xrange(kwargs.get('wait', 1)):
            time.sleep(1)
            result = self.client.get_server(self.context)
            if result is None:
                LOG.info("case pass")
                return 'p', "case pass"
        else:
            LOG.info("case failed")
            return 'f', 'case failed'

    def teardown(self):
        LOG.info("teardown context")
