import os
import time
from lib.logger import write_log
from lib.sys_inter_act import exe_sys_cmd_get_echo


def parse_xml_rude(xml_file = './file.xml'):
    xml_list = list()
    if os.path.exists(xml_file):
        f_hd = open(xml_file, 'r')
        xml_list = f_hd.readlines()
        f_hd.close()
    else:
        write_log("failed. non-existent, please check " + xml_file)
    return xml_list


def write_xml_rude(xml_list = list(), xml_file = './file.xml'):
    try:
        f_hd = open(xml_file, 'w')
    except:
        return False
    f_hd.writelines(xml_list)
    f_hd.close()
    return True


def modify_xml_rude(modify_list = dict(), xml_file = './file.xml'):
    result_list = [False] * len(modify_list)
    xml_list = parse_xml_rude(xml_file)
    if len(xml_list) == 0:
        return False
    result_index = 0
    for modify_point in modify_list:
        for index in range(len(xml_list) - 1, -1, -1):
            if xml_list[index].find('<' + modify_point['anchor'][0] + '>') == -1:
                continue
            if modify_point['action'] == 'replace':
                xml_list[index] = '<' + modify_point['anchor'][0] + '>' + modify_point['content'] + \
                                  '</' + modify_point['anchor'][0] + '>' + '\n'
                result_list[result_index] = True
            if modify_point['action'] == 'add':
                xml_list[index] = modify_point['content'] + '\n' + xml_list[index]
                result_list[result_index] = True
            if modify_point['action'] == 'delete':
                xml_list.pop(index)
                result_list[result_index] = True
        result_index += 1
    exe_sys_cmd_get_echo('cp -f ' + xml_file + ' ' + xml_file + '_bak_' + str(int(time.time())))
    write_xml_rude(xml_list, xml_file)
    return result_list


# for test
if __name__ == "__main__":
    test_xml = parse_xml_rude('/search/odin/xujiang/vrqo_test/QueryOptimizer/vrqo.cfg')
    write_xml_rude(test_xml, '/search/odin/xujiang/vrqo_test/QueryOptimizer/vrqo.cfg')
    modify_list = [
        {
            "anchor": ["ListenPort"],
            "action": "replace",
            "content": "8033"
        },
        {
            "anchor": ["/Parameter"],
            "action": "add",
            "content": "<test>test data</test>"
        }]
    modify_xml_rude(modify_list, '/search/odin/xujiang/vrqo_test/QueryOptimizer/vrqo.cfg')
