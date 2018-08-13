import time
import logging
import common.Case as Case
import common.taf_log as taf_log
import common.SDKutils as SDK

LOG = logging.getLogger("testlog")


class ServerCreate(Case.base):
    def __init__(self):
        super(ServerCreate, self).__init__()
        self.SDKconnect = SDK.SDKbase()
        self.context = {}

    def __repr__(self):
        return "ServerCreate"

    def run(self, steps):
        steps_args = self.gen_args_list(steps)
        server = self.SDKconnect.create_server(**steps_args[0])
        self.context['server'] = server

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-1")
    def check_result(self, kwargs):
        sla_args = []
        for args in xrange(len(kwargs)):
            sla_args.append(kwargs[args].values()[0])
        for loop in range(sla_args[0]['wait']):
            time.sleep(1)
            server_status = self.SDKconnect.get_server(self.context['server']['id'])['vm_state']
            if server_status == sla_args[0].get('status'):
                LOG.info("case pass")
                _result = 'p'
                _notes = 'case pass'
                break
        else:
            LOG.info("case failed")
            _result = 'f'
            _notes = 'case failed'

        return _result, _notes

    def teardown(self):
        LOG.info("teardown in ServerCreate")
        self.SDKconnect.delete_server(self.context['server']['id'])

class ServerDelete(Case.base):
    def __init__(self):
        super(ServerDelete, self).__init__()
        self.SDK = SDK.SDKbase()
        self.context = None

    def __repr__(self):
        return "ServerDelete"

    @taf_log.debug_log
    def run(self, steps):
        steps_args = self.gen_args_list(steps)
        server = self.SDK.create_server_and_wait_active(**steps_args[0])
        print server
        if server:
            self.context = server
            self.SDK.delete_server(server['id'], **steps_args[1])

    @taf_log.debug_log
    @SDK.SDKbase.testlink(testlink_id="OS-2")
    def check_result(self, kwargs):
        for loop in xrange(kwargs.get('wait', 1)):
            time.sleep(1)
            result = self.SDK.get_server(self.context['id'])
            if result is None:
                LOG.info("case pass")
                _result = 'p'
                _notes = 'case pass'
                break
        else:
            LOG.info("case failed")
            _result = 'f'
            _notes = 'case failed'

        return _result, _notes
