import logging
import common.case_utils as CASE
import common.taf_log as taf_log
import common.SDKutils as SDK
import common.sla as SLA

LOG = logging.getLogger("testlog")


class ServerCreate(CASE.base):
    def __init__(self):
        super(ServerCreate, self).__init__()
        self.SDKconnect = SDK.SDKbase(admin=True)
        self.context = {}

    def __repr__(self):
        return "ServerCreate"

    def run(self, steps):
        steps_args = self.gen_args_list(steps)
        server = self.SDKconnect.create_server(**steps_args[0])
        self.context['server'] = server

    @taf_log.debug_log
    @CASE.base.testlink(testlink_id="OS-1")
    def check_result(self, kwargs):
        result = False
        sla_args = []
        for args in xrange(len(kwargs)):
            sla_args.append(kwargs[args].values()[0])
        step_result = SLA.wait_for_vm_stat(self.SDKconnect, self.context['server'], sla_args[0]['status'],
                                           sla_args[0]['wait'])
        vm_ip = self.SDKconnect.get_server_public_ip(self.context['server'])
        step_result = step_result and SLA.vm_check_linux_host(vm_ip, sla_args[1]['username'], sla_args[1]['password'])
        result = step_result or result

        if result is True:
            _result = 'p'
            _notes = 'case pass'
        else:
            _result = 'f'
            _notes = 'case failed'
        LOG.info(_notes)
        return _result, _notes

    def teardown(self):
        LOG.info("teardown in ServerCreate")
        self.SDKconnect.delete_server(self.context['server']['id'])


class ServerDelete(CASE.base):
    def __init__(self):
        super(ServerDelete, self).__init__()
        self.SDKconnect = SDK.SDKbase()
        self.context = {}

    def __repr__(self):
        return "ServerDelete"

    @taf_log.debug_log
    def run(self, steps):
        steps_args = self.gen_args_list(steps)
        try:
            print steps_args[0]
            server = self.SDKconnect.create_server_and_wait_active(**steps_args[0])
            if server:
                self.context['server'] = server
                self.SDKconnect.delete_server(server['id'], **steps_args[1])
        except Exception as e:
            print e

    @taf_log.debug_log
    @CASE.base.testlink(testlink_id="OS-2")
    def check_result(self, kwargs):
        result = False
        sla_args = []
        for args in xrange(len(kwargs)):
            sla_args.append(kwargs[args].values()[0])
        # If vm check is not exist, then result is True
        step_result = not SLA.vm_check_in_openstack(self.SDKconnect, self.context['server'])

        result = step_result or result

        if result is True:
            _result = 'p'
            _notes = 'case pass'
        else:
            _result = 'f'
            _notes = 'case failed'
        LOG.info(_notes)
        return _result, _notes
