import os
import sys
from proc.gen_job_config import gen_job_config_main, gen_job_config_module_conf_mod, gen_job_config_module_data_mod, \
    get_job_config_file_name, gen_job_config_module_start_script
from lib.sys_inter_act import check_is_local_server, exe_sys_cmd_v3, exe_sys_cmd, start_service
from lib.compile_proc import compile_cplus
from lib.json_proc import parse_json
from proc.package_fetch import get_job_ini, modify_job_ini, svn_get_package
from proc.package_configure import get_conf, gen_conf
from lib.logger import write_log


def env_prepare():
    pass


def module_install(deploy_info, conf_module_mod, local_path):
    if not get_job_ini(deploy_info['online_info']['module_machine'], deploy_info['online_info']['module_path'],
                       local_path):
        return False
    cfg_modify_info = parse_json(conf_module_mod)
    if not modify_job_ini(cfg_modify_info, local_path):
        return False
    if svn_get_package(local_path + '/job.ini', local_path) == '':
        return False
    if not compile_cplus(local_path):
        return False
    exe_sys_cmd('rm -rf  ' + local_path + '/' + deploy_info['service_info']['service_exe_path'] + '/data')
    exe_sys_cmd('ln -s ' + deploy_info['offline_data_info']['data_base_path'] + '  ' +
                local_path + '/' + deploy_info['service_info']['service_exe_path'] + '/data')
    return True


def module_configure(deploy_info, conf_module_mod, local_path):
    cfg_modify_info = parse_json(conf_module_mod)
    get_conf(deploy_info['online_info']['module_machine'], deploy_info['online_info']['module_conf'], local_path,
             cfg_modify_info)
    is_ok, conf_name = gen_conf(cfg_modify_info, local_path)
    exe_sys_cmd('cp -f ' + local_path + '/conf/*  ' + local_path + '/' + deploy_info['service_info']['service_exe_path'] + '/')
    return is_ok, conf_name


def module_data_modify(deploy_info, conf_data_mod):
    exe_sys_cmd('cp -f ' + os.path.join(sys.path[0], deploy_info['offline_data_info']['data_script']) + '  ' + sys.path[
        0] + '/')
    if not exe_sys_cmd_v3('python3  ' +
                          os.path.join(sys.path[0], os.path.basename(deploy_info['offline_data_info']['data_script'])) +
                          '  ' + conf_data_mod):
        return False
    return True


def module_start(deploy_info, local_path, job_id):
    is_ok = False
    module_type = deploy_info['service_info']['service_type']
    start_shell = 'start_shell_' + module_type + '.sh'
    exe_sys_cmd_v3('cp -f  ' + os.path.join(sys.path[0], start_shell) + '  ' +
                   local_path + '/' + deploy_info['service_info']['service_exe_path'])
    start_shell_param_list = parse_json(
        os.path.join(sys.path[0], 'start_shell_param' + module_type + '_' + job_id + '.json'))
    os.chdir(local_path + '/' + deploy_info['service_info']['service_exe_path'])
    if len(start_shell_param_list) == 0:
        return is_ok
    is_ok = True
    for start_shell_param in start_shell_param_list:
        start_script = local_path + '/' + deploy_info['service_info']['service_exe_path'] + '/' + \
                       start_shell + '  ' + start_shell_param
        if not start_service(module_type,
                             local_path + '/' + deploy_info['service_info']['service_exe_path'],
                             start_script, '0', deploy_info['service_info']['startup_time'])[0]:
            is_ok = False
    return is_ok


def processor(build_tag='', step=''):
    # gen job_config in control server
    mysql_info = {'mysql_user': 'main_project',
                  'mysql_password': 'main_project',
                  'mysql_ip': '10.134.104.40',
                  'mysql_port': 3306,
                  'mysql_database': 'main_project'}
    if step == 'gen_job_config':
        if build_tag != '':
            if not (gen_job_config_main(mysql_info, build_tag) and
                    gen_job_config_module_conf_mod(mysql_info, build_tag) and
                    gen_job_config_module_data_mod(mysql_info, build_tag) and
                    gen_job_config_module_start_script(mysql_info, build_tag)):
                sys.exit(1)
        sys.exit(0)
    # build step by step in test server
    conf_main, conf_module_mod, conf_data_mod = get_job_config_file_name(os.path.join(sys.path[0], 'conf/'), build_tag)
    deploy_info = parse_json(conf_main)
    if step not in deploy_info['deploy_info']['deploy_step'].keys() or \
            deploy_info['deploy_info']['deploy_step'][step] == '0':
        write_log('step ' + step + ' is illegal, skip')
        sys.exit(0)
    local_path = ''
    for server_info in deploy_info['offline_server_info']:
        if check_is_local_server(server_info['addr']):
            # local_path = server_info['deploy_path'] + '/' + deploy_info['service_info']['service_name'] + '/'
            local_path = server_info['deploy_path'] + '/'
            break
    if local_path == '':
        sys.exit(1)
    if not exe_sys_cmd_v3('mkdir -p ' + local_path):
        sys.exit(1)
    env_prepare()
    if step == 'is_establish':
        if not module_install(deploy_info, conf_module_mod, local_path):
            sys.exit(2)
    elif step == 'is_config':
        if not module_configure(deploy_info, conf_module_mod, local_path)[0]:
            sys.exit(3)
    elif step == 'is_data':
        if not module_data_modify(deploy_info, conf_data_mod):
            sys.exit(4)
    elif step == 'is_start':
        if not module_start(deploy_info, local_path, build_tag):
            sys.exit(5)
    elif step == 'is_dailybuild':
        from proc.package_deploy_dailybuild import gen_dailybuild
        is_ok, conf_name, dailybuild_file = gen_dailybuild(deploy_info, local_path)
        if not is_ok:
            sys.exit(5)
        else:
            print(dailybuild_file)


# for test
if __name__ == "__main__":
    processor('job_id', 'gen_job_config')
