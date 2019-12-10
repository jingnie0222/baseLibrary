import os
import sys
import re
from lib.sftp_inter_act import SFTPClient
from lib.sys_inter_act import exe_sys_cmd
from lib.sys_inter_act import exe_sys_cmd_get_echo
from lib.sys_inter_act import split_sys_cmd_echo
from lib.json_proc import parse_json
from lib.text_proc import modify_text
from lib.ABMF_proc import merge_QO_config


def regular_file_get(offline_data_conf):
    dir_list = []
    if offline_data_conf.get('dev_data') is None:
        return []
    for dev_data_info in offline_data_conf['dev_data']:
        if (dev_data_info.get('data_path') is None) or (len(dev_data_info['data_path']) == 0):
            continue
        re_path = re.compile('(?P<dir>base.*)/(?P<name>[^/]+)/*$')
        sftp_client = SFTPClient(dev_data_info['addr'], "22", dev_data_info['username'], dev_data_info['password'])
        for path in dev_data_info['data_path']:
            path_suffix = re.search(re_path, path)
            if path_suffix:
                file_dict = path_suffix.groupdict()
                exe_sys_cmd_get_echo('mkdir -p {}/{}'.format(offline_data_conf['data_modify_path'], file_dict['dir']))
                dir_list.append(file_dict['dir'])
                sftp_client.sftp_get(path, '{}/{}/{}'.format(offline_data_conf['data_modify_path'], file_dict['dir'],
                                                             file_dict['name']))
        sftp_client.close()
    return dir_list


def vr_info_adjust(offline_data_conf):
    if (offline_data_conf.get('pre_server_info') is None):
        return []
    if (offline_data_conf.get('vrqo_VRInfo') is None) or \
            (offline_data_conf['vrqo_VRInfo'].get('class_ids') is None) or \
            (len(offline_data_conf['vrqo_VRInfo']['class_ids']) == 0):
        return []
    class_ids = offline_data_conf['vrqo_VRInfo']['class_ids']
    base_path = offline_data_conf['data_base_path']
    target_path = offline_data_conf['data_modify_path']
    pre_server_info = offline_data_conf['pre_server_info']
    dir_list = ['base/norm']
    vr_info_base = '{}/base/norm/vrqo_VRInfo'.format(base_path)
    exe_sys_cmd_get_echo('mkdir -p {}/base/norm'.format(target_path))
    exe_sys_cmd_get_echo('cp -f {} {}/base/norm/'.format(vr_info_base, target_path))
    vr_info_pre = '{}/base/norm/vrqo_VRInfo.pre'.format(target_path)
    sftp_client = SFTPClient(pre_server_info['addr'], "22", pre_server_info['username'], pre_server_info['password'])
    sftp_client.sftp_get('/search/odin/daemon/vrqo/data/base/norm/vrqo_VRInfo', vr_info_pre)
    sftp_client.close()
    info_dict = {}
    modify_list = []
    if not os.path.exists(vr_info_pre):
        return []
    with open(vr_info_pre) as f:
        for line in f:
            infos = line.split('\t')
            info_dict.update({infos[1]: line.strip('\n')})

    for class_id in class_ids:
        modify_list.append({
            "anchor": ['^{}'.format(class_id)],
            "action": "replace",
            "content": info_dict[class_id]
        })
    is_effect = modify_text(modify_list, '{}/base/norm/vrqo_VRInfo'.format(target_path))
    second_modify_list = []
    for i in range(len(is_effect)):
        if is_effect[i] == 0:
            second_modify_list.append({
                "anchor": ['$'],
                "action": "append",
                "content": info_dict[class_ids[i]]
            })
    modify_text(second_modify_list, '{}/base/norm/vrqo_VRInfo'.format(target_path))
    return dir_list


def qo_config_adjust(offline_data_conf):
    if (offline_data_conf.get('pre_server_info') is None):
        return []
    if (offline_data_conf.get('vrqo_QOConfig') is None) or \
            (offline_data_conf['vrqo_QOConfig'].get('class_ids') is None) or \
            (len(offline_data_conf['vrqo_QOConfig']['class_ids']) == 0):
        return []
    class_ids = offline_data_conf['vrqo_QOConfig']['class_ids']
    base_path = offline_data_conf['data_base_path']
    target_path = offline_data_conf['data_modify_path']
    pre_server_info = offline_data_conf['pre_server_info']
    dir_list = ['base/norm']
    qo_config_base = '{}/base/norm/vrqo_QOConfig'.format(base_path)
    qo_config_target = '{}/base/norm/vrqo_QOConfig'.format(target_path)
    qo_config_pre = '{}/base/norm/vrqo_QOConfig.pre'.format(target_path)
    exe_sys_cmd_get_echo('mkdir -p {}/base/norm'.format(target_path))
    exe_sys_cmd_get_echo('cp -f {} {}/base/norm/'.format(qo_config_base, target_path))
    sftp_client = SFTPClient(pre_server_info['addr'], "22", pre_server_info['username'], pre_server_info['password'])
    sftp_client.sftp_get('/search/odin/daemon/vrqo/data/base/norm/vrqo_QOConfig', qo_config_pre)
    sftp_client.close()
    pattern_names = []
    rule_names = []
    for class_id in class_ids:
        cmd_echo = exe_sys_cmd_get_echo('fgrep {} {}|fgrep "PATTERN_NAME"'.format(class_id, qo_config_target))
        if cmd_echo != '':
            pattern_names += cmd_echo.split('\n')
        cmd_echo = exe_sys_cmd_get_echo('fgrep {} {}|fgrep "RULE_NAME"'.format(class_id, qo_config_target))
        if cmd_echo != '':
            rule_names += cmd_echo.split('\n')
    merge_QO_config(qo_config_pre, qo_config_target,
                    [{"start": "<PATTERN NEW>", "end": "<PATTERN END>",
                      "key": "PATTERN_NAME"},
                     {"start": "<RULE NEW>", "end": "<RULE END>",
                      "key": "RULE_NAME"}],
                    {'<PATTERN NEW>': pattern_names,
                     '<RULE NEW>': rule_names}
                    )
    return dir_list


def vr_type_adjust(offline_data_conf):
    if (offline_data_conf.get('vrqo_TransVrType') is None) or \
            (len(offline_data_conf['vrqo_TransVrType']) == 0):
        return []
    vrqo_TransVrType_base = '{}/base/vrqo_TransVrType'.format(offline_data_conf['data_base_path'])
    vrqo_TransVrType_target = '{}/base/vrqo_TransVrType'.format(offline_data_conf['data_modify_path'])
    exe_sys_cmd_get_echo('mkdir -p {}/base/'.format(offline_data_conf['data_modify_path']))
    exe_sys_cmd_get_echo('cp -f ' + vrqo_TransVrType_base + '  ' + vrqo_TransVrType_target)
    modify_list = offline_data_conf['vrqo_TransVrType']
    modify_text(modify_list, vrqo_TransVrType_target)
    return ['base']


def vr_file_get(offline_data_conf):
    if (offline_data_conf.get('pre_server_info') is None):
        return []
    if (offline_data_conf.get('vr_files') is None) or \
            (offline_data_conf['vr_files'].get('class_ids') is None) or \
            (len(offline_data_conf['vr_files']['class_ids']) == 0):
        return []
    class_ids = offline_data_conf['vr_files']['class_ids']
    target_path = offline_data_conf['data_modify_path']
    pre_server_info = offline_data_conf['pre_server_info']
    sftp_client = SFTPClient(pre_server_info['addr'], "22", pre_server_info['username'], pre_server_info['password'])
    dir_list = ['base/vr/bin']
    exe_sys_cmd_get_echo('mkdir -p {}/base/vr/bin'.format(target_path))
    for class_id in class_ids:
        if class_id[0] == '7':
            file_re = class_id[:6]
        else:
            file_re = class_id
        ssh_echo, err = sftp_client.exe_ssh_cmd_get_echo('ls /search/odin/daemon/vrqo/data/base/vr/*{}*')
        if err == '':
            files = ssh_echo.format(file_re).strip('\n').split('\n')
            for file in files:
                sftp_client.sftp_get('/search/odin/daemon/vrqo/data/base/vr/*{}*'.format(file),
                                     '{}/base/vr/bin/'.format(target_path))
    sftp_client.close()
    return dir_list


def mk_data_file_link(offline_data_conf):
    if not offline_data_conf['need_data_modify']:
        return
    if offline_data_conf['data_modify_path'] == '':
        offline_data_conf['data_modify_path'] = sys.path[0] + '/test_data/'
        module_path = os.path.join(sys.path[0], 'dailybuild/opt/sogou/')
    else:
        module_path = os.path.join(offline_data_conf['service_info']['service_deploy_path'],
                                   offline_data_conf['service_info']['service_name'],
                                   offline_data_conf['service_info']['service_exe_path'])
    exe_sys_cmd('rm -rf  ' + module_path + '/data')
    exe_sys_cmd('rm -rf ' + offline_data_conf['data_modify_path'])
    exe_sys_cmd('mkdir -p  ' + offline_data_conf['data_modify_path'])
    exe_sys_cmd('ln -s ' + offline_data_conf['data_modify_path'] + '  ' + module_path + '/data')
    dir_list_all = list()
    dir_list_all += regular_file_get(offline_data_conf)
    dir_list_all += vr_info_adjust(offline_data_conf)
    dir_list_all += qo_config_adjust(offline_data_conf)
    dir_list_all += vr_type_adjust(offline_data_conf)
    dir_list_all += vr_file_get(offline_data_conf)
    for index in range(len(dir_list_all) - 1, -1, -1):
        if dir_list_all[index] in dir_list_all[:index]:
            dir_list_all.pop(index)
    for loop_id_1 in range(len(dir_list_all)):
        for loop_id_2 in range(loop_id_1 + 1, len(dir_list_all)):
            if len(dir_list_all[loop_id_1].split('/')) < len(dir_list_all[loop_id_2].split('/')):
                dir_list_all[loop_id_1], dir_list_all[loop_id_2] = dir_list_all[loop_id_2], dir_list_all[loop_id_1]
    for it in dir_list_all:
        if (re.search('base/vr$', it) is not None) or (re.search('base/vr/$', it) is not None):
            file_prefix_list = split_sys_cmd_echo(exe_sys_cmd_get_echo('ls | grep -o ^... | sort -u'), 0)
            for file_prefix in file_prefix_list:
                exe_sys_cmd(' ln -s  ' + offline_data_conf['data_base_path'] + '/' + it + '/' + file_prefix + '*  ' +
                                     offline_data_conf['data_modify_path'] + '/' + it + '/' + file_prefix + '*')
        else:
            exe_sys_cmd(' ln -s  ' + offline_data_conf['data_base_path'] + '/' + it + '/*  ' +
                             offline_data_conf['data_modify_path'] + '/' + it + '/')


if __name__ == "__main__":
    if len(sys.argv) == 2:
        data_modify_file = sys.argv[1]
        if os.path.exists(data_modify_file):
            offline_data_conf = parse_json(data_modify_file)
            if os.path.exists(offline_data_conf['data_base_path']):
                os.chdir(offline_data_conf['data_base_path'])
                exe_sys_cmd_get_echo('sh  Down.sh')
            else:
                sys.exit(1)
            mk_data_file_link(offline_data_conf)
