import openstack.connection as connection
import functools
import logging
from common import auth

LOG = logging.getLogger('testlog')

class base(object):
    def __init__(self):
        self.result = None

    def gen_args_list(self, kwargs):
        steps_args = []
        for step in range(len(kwargs)):
            steps_args.append(kwargs[step].values()[0])
        return steps_args

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
