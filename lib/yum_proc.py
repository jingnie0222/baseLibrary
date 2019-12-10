import os
import re
from lib.sys_inter_act import exe_sys_cmd_v3
from lib.ini_proc import parse_ini


def yum_install_local(package_list):
    result_list = list()
    for package in package_list:
        if package != '':
            result_list.append(exe_sys_cmd_v3('yum install -y ' + package))
    if False in result_list:
        return False
    else:
        return True


def yum_install_ssh(package_list, ssh_handle):
    result_list = list()
    for package in package_list:
        if package != '':
            echo, err = ssh_handle.exe_ssh_cmd_get_echo('yum install -y ' + package)
            if err == '':
                result_list.append(True)
            else:
                result_list.append(False)
    if False in result_list:
        return False
    else:
        return True


def yum_install_referto_jobini(job_ini = '', install_method = '', ssh_handle = None):
    is_ok = False
    if os.path.exists(job_ini):
        job_ini_dict = parse_ini(job_ini)
        if (job_ini_dict.get('main') is not None) and (job_ini_dict['main'].get('build_requires') is not None):
            yum_package_list = re.split('\s+|\t+', job_ini_dict['main']['build_requires'])
            if install_method == 'local':
                is_ok = yum_install_local(yum_package_list)
            elif install_method == 'remote':
                is_ok = yum_install_ssh(yum_package_list, ssh_handle)
    return is_ok


# for test
if __name__ == "__main__":
    yum_install_local(['protobuf', 'protobuf-devel'])
    yum_install_referto_jobini('./job.ini', 'local')

    from lib.ssh_inter_act import SSHClient
    ssh_client = SSHClient('10.134.104.61', "22",'root', 'test')
    yum_install_ssh(['protobuf', 'protobuf-devel'], ssh_client)
    yum_install_referto_jobini('./job.ini', 'remote', ssh_client)
    ssh_client.close()
