import ssh

def vm_check(ip, login_name, password, port=22, **kwargs):
    conn = ssh.SSH(ip, login_name, password, port, **kwargs)
    result = conn.exe_cmd('hostname')
    if result:
        return True
    else:
        return False