import time
import random
import logging
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
        try:
            step = 0
            values = kwargs[step].values()
            server = self._boot_server(**values[0])
            self.context = server['id']
        except:
            LOG.error("Create VM error!")
            raise

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-1")
    def sla(self, kwargs):
        for loop in range(kwargs.get('wait', 1)):
            time.sleep(1)
            server_status = self._get_server(self.context)['vm_state']
            if server_status == kwargs.get('status'):
                LOG.info("case pass")
                return 'p', 'case pass'
        else:
            LOG.info("case failed")
            return 'f', 'case failed'

    def teardown(self):
        LOG.info("teardown in ServerCreate")
        self._delete_server(self.context)


class ServerDelete(SDK.SDKbase):
    def __init__(self):
        super(ServerDelete, self).__init__()
        self.context = None

    def __repr__(self):
        return "ServerDelete"

    @taf_log.debug_log
    def run(self, kwargs):
        server = self._boot_server(**kwargs[0].values()[0])
        self.context=server['id']
        result = self._delete_server(server['id'], **kwargs[1].values()[0])
        if result:
            LOG.info('VM delete')
        else:
            LOG.error('VM delete error!')

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-2")
    def sla(self, kwargs):
        for loop in xrange(kwargs.get('wait', 1)):
            time.sleep(1)
            result = self._get_server(self.context)
            if result is None:
                LOG.info("case pass")
                return 'p', "case pass"
        else:
            LOG.info("case failed")
            return 'f', 'case failed'

    def teardown(self):
        LOG.info("teardown context")
