from keystoneauth1.identity import v3
from keystoneauth1 import session

import TestCase.config as config

def get_session(configfile=config):
    d = configfile
    auth = v3.Password(auth_url=d['auth_url'],
                       username=d['username'],
                       password=d['password'],
                       project_name="admin",
                       user_domain_id=d['user_domain_id'],
                       project_domain_id=d['project_domain_id'])
    sess = session.Session(auth=auth)
    return sess

def get_auth_info(configfile=config):
    """
    get openstack auth info
    :param configfile: auth_url, project_name, username, password, user_domain_name, project_domain_name
    :return:
    """
    d = {'auth_url': configfile.auth_url,
         'project_name': configfile.project_name,
         'username': configfile.username,
         'password': configfile.password,
         'user_domain_name': configfile.user_domain_name,
         'project_domain_name': configfile.project_domain_name}
    return d

def get_admin_auth_info(configfile=config):
    d = {'auth_url': configfile.auth_url,
         'project_name': configfile.project_name,
         'username': configfile.admin_user,
         'password': configfile.admin_password,
         'user_domain_name': configfile.user_domain_name,
         'project_domain_name': configfile.project_domain_name}
    return d