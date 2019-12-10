import paramiko
from lib.logger import write_log


def ssh_alive(func):
    def wrapper(self, *args, **kwargs):
        if self.ssh_is_alive:
            return func(self, *args, **kwargs)
    return wrapper


class SSHClient:
    def  __init__(self, ip,  port, user, password):
        self.ssh_conn = paramiko.SSHClient()
        self.ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_is_alive = False
        try:
            self.ssh_conn.connect(ip, port, user, password)
            self.ssh_is_alive = True
        except Exception as err:
            write_log(err)

    @ssh_alive
    def close(self):
        self.ssh_conn.close()

    @ssh_alive
    def exe_ssh_cmd_get_echo(self, os_cmd = ''):
        cmd_echo = ''
        cmd_echo_err = ''
        if os_cmd != '':
            write_log(os_cmd)
            stdin, stdout, stderr = self.ssh_conn.exec_command(os_cmd)
            if len(stderr.read()) == 0:
                cmd_echo = bytes.decode(stdout.read())
                write_log(cmd_echo)
            else:
                cmd_echo_err = bytes.decode(stderr.read())
                write_log(bytes.decode(stderr.read()))
        return cmd_echo, cmd_echo_err


# for test
if __name__ == "__main__":
    test_ssh_client = SSHClient('10.134.91.94',"22","root","noSafeNoWork@2014")
    echo, err = test_ssh_client.exe_ssh_cmd_get_echo('ls  -rtl ')
    #test_ssh_client.exe_ssh_cmd_get_echo('cd /search/odin/xujiang/vrqo_test/QueryOptimizer; nohup ./vrqo vrqo.cfg.ex  >std.ex.diff 2>err.ex.diff &')
    test_ssh_client.close()

    from lib.sys_inter_act import split_sys_cmd_echo
    echo_split_to_list = split_sys_cmd_echo(echo)
    write_log(echo_split_to_list)
    echo_split_to_list_partial = split_sys_cmd_echo(echo, 5)
    write_log(echo_split_to_list_partial)