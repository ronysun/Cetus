import paramiko
import time
import logging

LOG = logging.getLogger("testlog")

class SSH(paramiko.SSHClient):
    def __init__(self, ip, username, password, port):
        super(SSH, self).__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for loop in range(5):
            time.sleep(1)
            try:
                self.connect(ip, port, username, password)
                LOG.info("ssh connect create success")
                break
            except Exception as e:
                LOG.error(e)


    def exe_cmd(self, cmd):
        stdin, stdout, stderr = self.exec_command(cmd)
        return stdout.read()
