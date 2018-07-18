import openstack
import TestCase.config as config
from common import auth


class SDKbase(object):
    def __init__(self):
        auth_info = auth.get_auth_info()
        self.client = openstack.connection.Connection(**auth_info)