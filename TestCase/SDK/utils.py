import openstack
import functools
from common import auth


class SDKbase(object):
    def __init__(self):
        auth_info = auth.get_auth_info()
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