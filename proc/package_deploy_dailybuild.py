import os
import sys
import time
from lib.sys_inter_act import exe_sys_cmd
from lib.sftp_inter_act import SFTPClient
from lib.yum_proc import yum_install_referto_jobini
from lib.json_proc import parse_json
from lib.compile_proc import compile_dailybuild
from proc.package_fetch import get_job_ini, modify_job_ini, svn_get_package
from proc.package_configure import get_conf, gen_conf


def env_prepare():
    pass


def gen_dailybuild(deploy_info, local_path):
    is_ok = False
    conf_name = ''
    dailybuild_file = ''
    get_job_ini(deploy_info['online_info']['module_machine'], deploy_info['online_info']['module_path'], local_path)
    cfg_modify_info = parse_json(os.path.join(sys.path[0], deploy_info['config_modify_file']))
    modify_job_ini(cfg_modify_info, local_path)
    if svn_get_package(local_path + '/job.ini', local_path) != '':
        get_conf(deploy_info['online_info']['module_machine'], deploy_info['online_info']['module_conf'], local_path,
                 cfg_modify_info)
        is_ok, conf_name = gen_conf(cfg_modify_info, local_path)
        is_ok, dailybuild_file = compile_dailybuild(local_path + '/job.ini', local_path)
    return is_ok, conf_name, dailybuild_file


def distribute_dailybuild(server_info_list, dailybuild_file = '', local_path = '', remote_path = '', remote_data_path = '', build_tag = ''):
    result_list = [False] * len(server_info_list)
    result_index = 0
    if os.path.exists(dailybuild_file):
        for server_info in server_info_list:
            if remote_path == '':
                distribute_path = server_info['deploy_path']
            else:
                distribute_path = remote_path
            distribute_path = os.path.join(distribute_path, build_tag)
            sftp_client = SFTPClient(server_info['addr'], "22", server_info['username'], server_info['password'])
            if not yum_install_referto_jobini(local_path + '/job.ini', 'remote', sftp_client):
                continue
            sftp_client.sftp_rmdir(distribute_path)
            sftp_client.sftp_mkdir(distribute_path)
            sftp_client.sftp_put(dailybuild_file, distribute_path)
            if '' == sftp_client.exe_ssh_cmd_get_echo(
                    'tar -xf ' + distribute_path + '/dailybuild.tar.gz  -C ' + distribute_path + '/')[1]:
                sftp_client.exe_ssh_cmd_get_echo('rm -f ' + os.path.join(distribute_path, 'dailybuild/opt/sogou/data'))
                sftp_client.exe_ssh_cmd_get_echo(
                    'ln -s ' + remote_data_path + '  ' + os.path.join(distribute_path, 'dailybuild/opt/sogou/data'))
                result_list[result_index] = True
            sftp_client.close()
            result_index += 1
        if False not in result_list:
            return True
    return False


def distribute_customized_data(server_info_list, offline_data_info, remote_path = '', build_tag = ''):
    result_list = [False] * len(server_info_list)
    result_index = 0
    for server_info in server_info_list:
        if remote_path == '':
            distribute_path = server_info['deploy_path']
        else:
            distribute_path = remote_path
        distribute_path = os.path.join(distribute_path, build_tag)
        data_script = os.path.join(sys.path[0], offline_data_info['data_script'])
        data_conf = os.path.join(sys.path[0], offline_data_info['data_conf'])
        if os.path.exists(data_script) and os.path.exists(data_conf):
            sftp_client = SFTPClient(server_info['addr'], "22", server_info['username'], server_info['password'])
            sftp_client.sftp_mkdir(distribute_path)
            sftp_client.sftp_put(data_script, distribute_path)
            sftp_client.sftp_put(data_conf, distribute_path)
            sftp_client.sftp_put(os.path.join(sys.path[0], 'lib'), distribute_path + '/lib/')
            if '' == sftp_client.exe_ssh_cmd_get_echo('python3  ' +
                                             os.path.join(distribute_path,
                                                          os.path.basename(
                                                              data_script)) + '  ' +
                                             os.path.join(distribute_path,
                                                          os.path.basename(data_conf)))[1]:
                result_list[result_index] = True
            sftp_client.close()
        result_index += 1
    if False not in result_list:
        return True
    return False


def start_module_service(server_info_list, remote_path = '', module_name = '', conf_name = '', build_tag = ''):
    from start_shell.gen_start_shell import gen_start_shell_vrqo_dailybuild
    result_list = [False] * len(server_info_list)
    result_index = 0
    for server_info in server_info_list:
        if remote_path == '':
            distribute_path = server_info['deploy_path']
        else:
            distribute_path = remote_path
        distribute_path = os.path.join(distribute_path, build_tag)
        start_shell = 'start_shell_' + module_name + '.sh'
        if not eval('gen_start_shell_' + module_name + '_dailybuild')(conf_name):
            result_index += 1
            continue
        sftp_client = SFTPClient(server_info['addr'], "22", server_info['username'], server_info['password'])
        sftp_client.sftp_put(os.path.join(sys.path[0], start_shell), distribute_path + '/dailybuild/opt/sogou/')
        if '' == sftp_client.exe_ssh_cmd_get_echo('cd ' + distribute_path + '/dailybuild/opt/sogou/' + ' && ' + 'sh ' + start_shell)[1]:
            result_list[result_index] = True
        sftp_client.close()
        result_index += 1
    if False not in result_list:
        return True
    return False


def processor(deploy_conf, build_tag = ''):
    deploy_info = parse_json(deploy_conf)
    env_prepare()
    if build_tag == '':
        build_tag = str(int(time.time()))
    local_path = deploy_info['deploy_info']['deploy_local_path'] + '/' + build_tag + '/'
    exe_sys_cmd('mkdir -p ' + local_path)
    is_ok, conf_name, dailybuild_file = gen_dailybuild(deploy_info, local_path)
    if not is_ok:
        sys.exit(2)
    if not distribute_dailybuild(deploy_info['offline_server_info'], dailybuild_file, local_path, '', deploy_info['offline_data_info']['data_base_path'], build_tag):
        sys.exit(3)
    if not distribute_customized_data(deploy_info['offline_server_info'], deploy_info['offline_data_info'], '', build_tag):
        sys.exit(4)
    if not start_module_service(deploy_info['offline_server_info'], '', deploy_info['service_info']['service_name'], conf_name, build_tag):
        sys.exit(5)


# for test
if __name__ == "__main__":
    processor('./conf/conf_template.json', 'test')
