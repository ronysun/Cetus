import openstack
import functools
import logging
from common import auth

LOG = logging.getLogger('testlog')

class SDKbase(object):
    def __init__(self, auth_info=auth.get_auth_info(), admin=False):
        if admin:
            auth_info = auth.get_admin_auth_info()
        self.client = openstack.connection.Connection(**auth_info)
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

    def _boot_server(self, name, image, flavor, **kwargs):
        try:
            server = self.client.create_server(name, image=image, flavor=flavor, **kwargs)
            return server
        except Exception as e:
            LOG.error(e)

    def _delete_server(self, name_or_id, **kwargs ):
        return self.client.delete_server(name_or_id, **kwargs)

    def _get_server(self, name_or_id, **kwargs):
        return self.client.get_server(name_or_id, **kwargs)

    def _image_create(self, name, **kwargs):
        return self.client.create_image(name, **kwargs)

    def _flavor_create(self, name, ram, vcpus, disk, **kwargs):
        return self.client.create_flavor(name, ram, vcpus, disk, **kwargs)
