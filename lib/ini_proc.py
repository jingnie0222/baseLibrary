import os
import time
from configparser import ConfigParser
from collections import defaultdict
from lib.logger import write_log
from lib.sys_inter_act import exe_sys_cmd_get_echo


def _tree():
    return defaultdict(_tree)


def parse_ini(ini_file = './file.ini'):
    ini_dict = _tree()
    if os.path.exists(ini_file):
        parser = ConfigParser()
        try:
            parser.read(ini_file)
        except:
            write_log("failed. parse ini file error, please check " + ini_file)
            return ini_dict
        section_list = parser.sections()
        for section in section_list:
            param_list = parser.options(section)
            for param in param_list:
                ini_dict[section][param] = parser[section][param]
    else:
        write_log("failed. non-existent or non-ini-format , please check " + ini_file)
    return ini_dict


def write_ini(data = dict(), ini_file = './file.ini'):
    parser = ConfigParser()
    try:
        parser.read_dict(data)
    except:
        write_log("failed. parse ini data error, please check " + str(data))
        return False
    try:
        f_hd = open(ini_file, 'w')
    except:
        return False
    try:
        parser.write(f_hd)
    except:
        f_hd.close()
        return False
    f_hd.close()
    return True


def modify_ini(modify_list, ini_file = './file.ini'):
    result_list = [False] * len(modify_list)
    ini_dict = parse_ini(ini_file)
    if len(ini_dict) == 0:
        return result_list
    result_index = 0
    for modify_point in modify_list:
        if len(modify_point['anchor']) == 2:
            section = modify_point['anchor'][0]
            param = modify_point['anchor'][1]
            value = modify_point['content']
            if modify_point['action'] == 'replace':
                if ini_dict.get(section) is not None and ini_dict[section].get(param) is not None:
                    ini_dict[section][param] = value
                    result_list[result_index] = True
            if modify_point['action'] == 'add':
                if ini_dict.get(section) is not None:
                    if ini_dict[section].get(param) is not None:
                        ini_dict[section][param] = ini_dict[section][param] + ' ' + value
                    else:
                        ini_dict[section][param] = value
                else:
                    ini_dict[section] = {param:value}
                result_list[result_index] = True
            if modify_point['action'] == 'delete':
                if ini_dict.get(section) is not None:
                    if param == '':
                        ini_dict.pop(section)
                        result_list[result_index] = True
                    elif ini_dict[section].get(param) is not None:
                        ini_dict[section].pop(param)
                        result_list[result_index] = True
        result_index += 1
    exe_sys_cmd_get_echo('cp -f ' + ini_file + ' ' + ini_file + '_bak_' + str(int(time.time())))
    write_ini(ini_dict, ini_file)
    return result_list


# for test
if __name__ == "__main__":
    test_ini = parse_ini('./job.ini')
    write_ini(test_ini, './job.ini.new')
    modify_list = [
        {
            "anchor": ["main", "build_requires"],
            "action": "add",
            "content": "pcre2 pcre2-devel"
        },
        {
            "anchor": ["main.svn", "."],
            "action": "replace",
            "content": "http://svn.sogou-inc.com/svn/websearch4/VH/vr_QO/branches/opt_vrqo.20191014"
        }
    ]
    modify_ini(modify_list, './job.ini')