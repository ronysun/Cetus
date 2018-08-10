import paramiko


# ssh = paramiko.SSHClient()


class SSH(object):
    def __init__(self, ip, login_name, password, port=22, **kwargs):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username=login_name, password=password, **kwargs)
        self.client = ssh

    def exe_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.read().strip("\n")

