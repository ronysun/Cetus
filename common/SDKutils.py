import time
import openstack.connection as connection
import functools
import logging
from common import auth

LOG = logging.getLogger('testlog')

class SDKbase(connection.Connection):
    def __init__(self, auth_info=auth.get_auth_info(), admin=False):
        if admin:
            auth_info = auth.get_admin_auth_info()
        super(SDKbase, self).__init__(
                 **auth_info)
        self.result = None

    @staticmethod
    def testlink(testlink_id=None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs), testlink_id

            return wrapper

        return decorator

    def setup(self):
        pass

    def teardown(self):
        pass

    def get_step_args(self, args_list):
        pass

    def create_server_and_wait_active(self, wait_time, **kwargs):
        server = self.create_server(**kwargs)
        for loop in range(wait_time):
            time.sleep(1)
            server_status = self.get_server(server['id'])['vm_state']
            if server_status == 'active':
                return server
        else:
            LOG.info('server: %s is not active in %ss' % (server['name'], wait_time))
            self.delete_server(server['id'])
            return False