import os
import sys
import re
import json
from lib.mysql_interaction import MYSQLClient
from lib.json_proc import parse_json, write_json
from lib.sys_inter_act import exe_sys_cmd_get_echo_v3
from lib.common_function import trim_head_tail


def gen_job_config_main(mysql_info, job_id = ''):
    is_ok = False
    mysql_client = MYSQLClient(mysql_info['mysql_user'], mysql_info['mysql_password'], mysql_info['mysql_ip'],
                               mysql_info['mysql_port'], mysql_info['mysql_database'])
    status, title, data = mysql_client.execute_sql('select * from offline_mission_info where mission_id = ' + job_id)
    deploy_step = {}
    if status and len(title) > 0 and len(data) == 1:
        module_type = data[0][title.index('module')]
        for column_name in title:
            if re.search('^is_', column_name) is not None:
                deploy_step[column_name] = str(data[0][title.index(column_name)])
    else:
        return is_ok
    if len(deploy_step) == 0:
        return is_ok
    template_file = sys.path[0] + '/conf/conf_template_' + module_type + '.json'
    config_dict = parse_json(template_file)
    if len(config_dict) == 0:
        return is_ok
    config_dict['service_info']['service_name'] = module_type
    config_dict['service_info']['service_type'] = module_type
    config_dict['deploy_info']['deploy_step'] = deploy_step
    config_dict['deploy_info']['deploy_local_path'] = config_dict['deploy_info']['deploy_local_path'] + '/' + job_id + '/'
    status, title, data = mysql_client.execute_sql(
        'select * from offline_module_config_info where module = "' + module_type + '"')
    if status and len(title) > 0 and len(data) == 1:
        config_dict['service_info']['startup_time'] = int(data[0][title.index('max_start_time')])
    config_dict['offline_server_info'].clear()
    status, title, data = mysql_client.execute_sql('select * from offline_machine_info where mission_id = ' + job_id)
    if status and len(title) > 0 and len(data) > 0:
        for it in data:
            addr = it[title.index('ip')]
            deploy_path = it[title.index('path')]
            it_status, it_title, it_data = mysql_client.execute_sql('select * from offline_machine_config where ip = "' + addr + '"')
            if it_status and len(it_title) > 0 and len(it_data) == 1:
                username = it_data[0][it_title.index('user')]
                password = it_data[0][it_title.index('passwd')]
                config_dict['offline_server_info'].append({"addr": addr,
                                                           "username": username,
                                                           "password": password,
                                                           "deploy_path": deploy_path})
    mysql_client.close()
    if len(config_dict['offline_server_info']) > 0:
        is_ok = True
    config_dict['offline_data_info']['data_conf'] = './conf/data_modify_' + module_type + '_' + job_id + '.json'
    config_dict['config_modify_file'] = './conf/config_modify_' + module_type + '_' + job_id + '.json'
    if not write_json(config_dict, sys.path[0] + '/conf/conf_' + module_type + '_' + job_id + '.json'):
        is_ok = False
    return is_ok


def gen_job_config_module_conf_mod(mysql_info, job_id):
    is_ok = False
    mysql_client = MYSQLClient(mysql_info['mysql_user'], mysql_info['mysql_password'], mysql_info['mysql_ip'],
                               mysql_info['mysql_port'], mysql_info['mysql_database'])
    status, title, data = mysql_client.execute_sql(
        'select * from offline_mission_info where mission_id = ' + str(job_id))
    if status and len(title) > 0 and len(data) == 1:
        module_type = data[0][title.index('module')]
    else:
        return is_ok
    config_dict = []
    modContent_jobini = list()
    status, title, data = mysql_client.execute_sql('select * from offline_env_info where mission_id = ' + job_id)
    if status and len(title) > 0 and len(data) > 0:
        for it in data:
            if it[title.index('key')] == 'yum':
                modContent_jobini.append({
                    "anchor": ["main", "build_requires"],
                    "action": it[title.index('action')],
                    "content": it[title.index('content')]
                })
            else:
                modContent_jobini.append({
                    "anchor": ["main.svn", it[title.index('key')]],
                    "action": it[title.index('action')],
                    "content": it[title.index('content')]
                })
    modContent_cfg_dict = dict()
    status, title, data = mysql_client.execute_sql('select * from offline_module_config_template where module = "' + module_type + '"')
    if status and len(title) > 0 and len(data) > 0:
        for it in data:
            modContent_cfg_dict[it[title.index('config_name')]] = (json.loads(it[title.index('config_edit')]), it[title.index('config_type')])
    for config_name in modContent_cfg_dict.keys():
        status, title, data = mysql_client.execute_sql(
            'select * from offline_config_info where mission_id = ' + job_id + ' and config_name = "' + config_name + '"')
        if status and len(title) > 0 and len(data) > 0:
            for it in data:
                modContent_cfg_dict[config_name][0].append({
                    "anchor": [it[title.index('key')]],
                    "action": it[title.index('action')],
                    "content": it[title.index('value')],
                })
    mysql_client.close()
    if len(modContent_jobini) > 0:
        config_dict.append(
            {
                "config_file": "job.ini",
                "config_type": "ini",
                "modContent": modContent_jobini
            })
        is_ok = True
    for config_name in modContent_cfg_dict.keys():
        if len(modContent_cfg_dict[config_name][0]) > 0:
            config_dict.append(
                {
                    "config_file": config_name,
                    "config_type": modContent_cfg_dict[config_name][1],
                    "enable": True,
                    "modContent": modContent_cfg_dict[config_name][0]
                })
            is_ok = True
        else:
            is_ok = False
    if not write_json(config_dict, sys.path[0] + '/conf/config_modify_' + module_type + '_' + job_id + '.json'):
        is_ok = False
    return is_ok


def gen_job_config_module_data_mod(mysql_info,  job_id):
    is_ok = False
    mysql_client = MYSQLClient(mysql_info['mysql_user'], mysql_info['mysql_password'], mysql_info['mysql_ip'],
                               mysql_info['mysql_port'], mysql_info['mysql_database'])
    status, title, data = mysql_client.execute_sql('select * from offline_mission_info where mission_id = ' + str(job_id))
    if status and len(title) > 0 and len(data) == 1:
        module_type = data[0][title.index('module')]
    else:
        return is_ok
    template_file = sys.path[0] + '/conf/data_modify_template_' + module_type + '.json'
    config_dict = parse_json(template_file)
    if len(config_dict) == 0:
        return is_ok
    config_dict['dev_data'][0]['data_path'].clear()
    status, title, data = mysql_client.execute_sql('select * from offline_data_info where mission_id = ' + job_id)
    if status and len(title) > 0 and len(data) > 0:
        for it in data:
            if it[title.index('key')] == 'data_path':
                config_dict['dev_data'][0]['data_path'].append(it[title.index('content')])
            else:
                try:
                    config_dict[it[title.index('key')]] = json.loads(it[title.index('content')])
                except:
                    config_dict[it[title.index('key')]] = {}
        config_dict['need_data_modify'] = True
        is_ok = True
    elif status:
        config_dict['need_data_modify'] = False
    deploy_server_info = dict()
    status, title, data = mysql_client.execute_sql('select * from offline_machine_info where mission_id = ' + job_id)
    if status and len(title) > 0 and len(data) > 0:
        for it in data:
            deploy_server_info[it[title.index('ip')]] = it[title.index('path')]
    mysql_client.close()
    for addr in deploy_server_info.keys():
        config_dict['service_info']['service_deploy_path'] = deploy_server_info[addr]
        config_dict['data_modify_path'] = deploy_server_info[addr] + '/test_data/'
        if not write_json(config_dict, sys.path[0] + '/conf/data_modify_' + module_type + '_' + job_id + '_' + addr + '.json'):
            is_ok = False
    return is_ok


def get_job_config_file_name(path = '', job_id = ''):
    conf_file = ''
    config_modify_file = ''
    data_modify_file = ''
    file, err_code = exe_sys_cmd_get_echo_v3('ls ' + path + '/conf_*_' + job_id + '.json')
    if err_code == 0:
        file = trim_head_tail(file)
        if os.path.exists(file):
            conf_file = file
    file, err_code = exe_sys_cmd_get_echo_v3('ls ' + path + '/config_modify_*_' + job_id + '.json')
    if err_code == 0:
        file = trim_head_tail(file)
        if os.path.exists(file):
            config_modify_file = file
    file, err_code = exe_sys_cmd_get_echo_v3('ls ' + path + '/data_modify_*_' + job_id + '_*.json')
    if err_code == 0:
        file = trim_head_tail(file)
        if os.path.exists(file):
            data_modify_file = file
    return conf_file, config_modify_file, data_modify_file


def gen_job_config_module_start_script(mysql_info, job_id):
    is_ok = False
    mysql_client = MYSQLClient(mysql_info['mysql_user'], mysql_info['mysql_password'], mysql_info['mysql_ip'],
                               mysql_info['mysql_port'], mysql_info['mysql_database'])
    status, title, data = mysql_client.execute_sql(
        'select * from offline_mission_info where mission_id = ' + str(job_id))
    if status and len(title) > 0 and len(data) == 1:
        module_type = data[0][title.index('module')]
    else:
        return is_ok
    start_shell_param_list = list()
    status, title, data = mysql_client.execute_sql(
        'select * from offline_start_info where mission_id = ' + job_id + ' and module = "' + module_type + '" ORDER BY id')
    if status and len(title) > 0 and len(data) > 0:
        for it in data:
            start_shell_param_list.append(it[title.index('start_param')])
    mysql_client.close()
    if len(start_shell_param_list) == 0:
        return is_ok
    if not write_json(start_shell_param_list, os.path.join(sys.path[0], 'start_shell_param' + module_type + '_' + job_id + '.json')):
        return is_ok
    from start_shell.gen_start_shell import gen_start_shell_from_sql
    return gen_start_shell_from_sql(mysql_info, module_type)


# for test
if __name__ == "__main__":
    mysql_info = {'mysql_user': 'main_project',
                  'mysql_password': 'main_project',
                  'mysql_ip': '10.134.104.40',
                  'mysql_port': 3306,
                  'mysql_database': 'main_project'}
    build_tag = '102'
    print('gen_job_config_main: ', gen_job_config_main(mysql_info, build_tag))
    print('gen_job_config_module_conf_mod: ', gen_job_config_module_conf_mod(mysql_info, build_tag))
    print('gen_job_config_module_data_mod: ', gen_job_config_module_data_mod(mysql_info, build_tag))
    print('gen_job_config_module_start_script: ', gen_job_config_module_start_script(mysql_info, build_tag))
