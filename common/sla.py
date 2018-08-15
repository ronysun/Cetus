import ssh


def vm_check_linux_host(ip, login_name, password, port=22):
    conn = ssh.SSH(ip, login_name, password, port)
    _result = conn.exe_cmd('cat /proc/cpuinfo')
    if _result is not '':
        return True
    else:
        return False


def vm_state_check_in_openstack(SDKconnect, server, state, wait_time=1):
    for loop in xrange(wait_time):
        if SDKconnect.get_server(server['id'])['vm_state'] == state:
            return True
    else:
        return False


def vm_check_in_openstack(SDKconnect, server):
    if SDKconnect.get_server(server['id']) is None:
        return False
    else:
        return True