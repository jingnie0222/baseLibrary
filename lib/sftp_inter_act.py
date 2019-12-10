import os
from lib.logger import write_log
from lib.ssh_inter_act import SSHClient
import shlex


def sftp_alive(func):
    def wrapper(self, *args, **kwargs):
        if self.sftp_is_alive:
            return func(self, *args, **kwargs)
    return wrapper


class SFTPClient(SSHClient):
    def __init__(self, ip, port, user, password):
        self.sftp_is_alive = False
        try:
            super().__init__(ip, port, user, password)
            self.sftp_conn = self.ssh_conn.open_sftp()
            self.sftp_is_alive = True
        except Exception as err:
            write_log(err)

    @sftp_alive
    def close(self):
        self.sftp_conn.close()
        super().close()

    @sftp_alive
    def sftp_mkdir(self, dir = ''):
        stdin, stdout, stderr = self.ssh_conn.exec_command('mkdir -p  ' + dir)
        if len(stderr.read()) == 0:
            write_log("ftp make  dir " + dir + " succ")
            return True
        else:
            write_log("ftp make  dir " + dir + " fail")
            return False

    @sftp_alive
    def sftp_rmdir(self, dir=''):
        stdin, stdout, stderr = self.ssh_conn.exec_command('rm  -rf  ' + dir)
        if len(stderr.read()) == 0:
            write_log("ftp remove  dir " + dir + " succ")
            return True
        else:
            write_log("ftp remove  dir " + dir + " fail")
            return False

    @sftp_alive
    def sftp_chdir(self, dir=''):
        try:
            self.sftp_conn.chdir(dir)
            return True
        except:
            return False

    @sftp_alive
    def sftp_get(self, remote_path, local_path, loop = False):
        if not self.sftp_chdir(remote_path):
            if loop:
                return
        if not os.path.isdir(local_path):
            os.system('rm  -f  ' + local_path)
        if not loop:
            remote_file = remote_path
            if os.path.isdir(local_path):
                local_file = os.path.join(local_path, os.path.basename(remote_path))
            else:
                local_file = local_path
            try:
                if self.exe_ssh_cmd_get_echo('ls ' + remote_file)[1] == '':
                    self.sftp_conn.get(remote_file, local_file)
            except:
                pass
            return
        os.system('mkdir  -p  ' + local_path)
        file_list = self.sftp_conn.listdir(remote_path)
        for file in file_list:
            remote_file = os.path.join(remote_path, file)
            local_file = os.path.join(local_path, file)
            try:
                if not os.path.isdir(local_file):
                    os.system('rm  -f  ' + shlex.quote(local_file))
                if self.exe_ssh_cmd_get_echo('ls ' + remote_file)[1] == '':
                    self.sftp_conn.get(remote_file, local_file)
            except:
                self.sftp_get(remote_file, local_file, True)

    @sftp_alive
    def sftp_put(self, local_path, remote_path, loop = False):
        if (not loop) and (not os.path.isdir(local_path)):
            local_file = local_path
            if os.path.basename(remote_path) == '':
                self.sftp_mkdir(remote_path)
                remote_file = os.path.join(remote_path, os.path.basename(local_path))
            else:
                self.sftp_mkdir(os.path.dirname(remote_path))
                remote_file = remote_path
            try:
                self.sftp_rmdir(remote_file)
                if os.path.exists(local_file):
                    self.sftp_conn.put(local_file, remote_file)
            except:
                pass
            return
        try:
            file_list = os.listdir(local_path)
        except:
            return
        self.sftp_mkdir(remote_path)
        for file in file_list:
            remote_file = os.path.join(remote_path, file)
            local_file = os.path.join(local_path, file)
            try:
                if not self.sftp_chdir(remote_file):
                    self.sftp_rmdir(remote_file)
                if os.path.exists(local_file):
                    self.sftp_conn.put(local_file, remote_file)
            except Exception as e:
                self.sftp_put(local_file, remote_file, True)


# for test
if __name__ == "__main__":
    test_sftp_client = SFTPClient('10.134.96.121',"22","root","noSafeNoWork@2014")
    test_sftp_client.sftp_get('/search/data/openhub_data','/search/odin/xujiang/test_2')
    test_sftp_client.sftp_put('/search/odin/xujiang/test_2', '/search/odin/xujiang/test_3')
    test_sftp_client.close()
