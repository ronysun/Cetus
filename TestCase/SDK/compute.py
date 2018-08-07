import time
import logging
import TestCase.config as config
import common.taf_log as taf_log
import TestCase.SDK.utils as SDK

LOG = logging.getLogger("testlog")


class ServerCreate(SDK.SDKbase):

    def __init__(self):
        super(ServerCreate, self).__init__()
        self.context = None

    def __repr__(self):
        return "ServerCreate"

    @taf_log.debug_log
    def run(self, kwargs):
        step = 0
        values = kwargs[step].values()
        # server = self.create_server(network=config.ex_network, **values[0])
        server = self.create_server(**values[0])
        if server:
            self.context = server

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-1")
    def sla(self, kwargs):
        for loop in range(kwargs.get('wait', 1)):
            time.sleep(1)
            server_status = self.get_server(self.context['id'])['vm_state']
            if server_status == kwargs.get('status'):

                LOG.info("case pass")
                return 'p', 'case pass'
        else:
            LOG.info("case failed")
            return 'f', 'case failed'

    def teardown(self):
        LOG.info("teardown in ServerCreate")
        # self.delete_server(self.context['id'])


class ServerDelete(SDK.SDKbase):
    def __init__(self):
        super(ServerDelete, self).__init__()
        self.context = None

    def __repr__(self):
        return "ServerDelete"

    @taf_log.debug_log
    def run(self, kwargs):
        server = self.create_server(**kwargs[0].values()[0])
        if server:
            self.context = server['id']
        result = self.delete_server(server['id'], **kwargs[1].values()[0])
        if result:
            LOG.info('VM delete')
        else:
            LOG.error('VM delete error!')

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-2")
    def sla(self, kwargs):
        for loop in xrange(kwargs.get('wait', 1)):
            time.sleep(1)
            result = self.get_server(self.context)
            if result is None:
                LOG.info("case pass")
                return 'p', "case pass"
        else:
            LOG.info("case failed")
            return 'f', 'case failed'

    def teardown(self):
        LOG.info("teardown context")
