import os
from lib.sys_inter_act import exe_sys_cmd_get_echo, exe_sys_cmd
from lib.xml_proc import modify_xml_rude


def get_conf(server = '', conf_online = '', local_path = '', config_modify_list = list()):
    exe_sys_cmd('mkdir -p ' + local_path + '/conf')
    exe_sys_cmd_get_echo('rsync -vazP ' + server + '::' + conf_online + '  ' + local_path + '/conf/conf_online')
    if os.path.exists(local_path + '/conf/conf_online'):
        for config_modify in config_modify_list:
            if config_modify['config_type'] == 'cfg':
                exe_sys_cmd_get_echo('cp -f ' + local_path + '/conf/conf_online  ' + local_path + '/conf/' + config_modify['config_file'])
        return True
    else:
        return False


def gen_conf(config_modify_list, local_path = ''):
    is_ok = False
    conf_name = ''
    for config_modify in config_modify_list:
        if os.path.exists(local_path + '/conf/' + config_modify['config_file']):
            if config_modify['config_type'] == 'cfg':
                result_list = modify_xml_rude(config_modify['modContent'], local_path + '/conf/' + config_modify['config_file'])
                if config_modify['enable']:
                    conf_name = config_modify['config_file']
                if False not in result_list:
                    is_ok = True
    return is_ok, conf_name
