import os
import time
import re
from lib.logger import write_log
from lib.sys_inter_act import exe_sys_cmd_get_echo


def parse_text(text_file = './file.text', encoding = 'utf8'):
    text_list = list()
    if os.path.exists(text_file):
        f_hd = open(text_file, 'r', encoding = encoding, errors='ignore')
        text_list = f_hd.readlines()
        f_hd.close()
    else:
        write_log("failed. non-existent, please check " + text_file)
    return text_list


def write_text(text_list = list(), text_file = './file.text', encoding = 'utf8'):
    try:
        f_hd = open(text_file, 'w', encoding = encoding, errors='ignore')
    except:
        return False
    f_hd.writelines(text_list)
    f_hd.close()
    return True


def modify_text(modify_list = dict(), text_file = './file.text', encoding = 'utf8'):
    result_list = [False] * len(modify_list)
    text_list = parse_text(text_file, encoding)
    if len(text_list) == 0:
        return result_list
    result_index = 0
    for modify_point in modify_list:
        if modify_point['action'] == 'tail':
            text_list.append(modify_point['content'] + '\n')
            result_list[result_index] = True
            result_index += 1
            continue
        if modify_point['action'] == 'head':
            text_list[0] = modify_point['content'] + '\n' + text_list[0]
            result_list[result_index] = True
            result_index += 1
            continue
        for index in range(len(text_list) - 1, -1, -1):
            if re.search(modify_point['anchor'][0], text_list[index]) is None:
                continue
            if modify_point['action'] == 'replace':
                text_list[index] = modify_point['content'] + '\n'
                result_list[result_index] = True
            if modify_point['action'] == 'append':
                text_list[index] = text_list[index] + modify_point['content'] + '\n'
                result_list[result_index] = True
            if modify_point['action'] == 'insert':
                text_list[index] = modify_point['content'] + '\n' + text_list[index]
                result_list[result_index] = True
            if modify_point['action'] == 'delete':
                text_list.pop(index)
                result_list[result_index] = True
        result_index += 1
    exe_sys_cmd_get_echo('cp -f ' + text_file + ' ' + text_file + '_bak_' + str(int(time.time())))
    write_text(text_list, text_file, encoding)
    return result_list


# for test
if __name__ == "__main__":
    test_text = parse_text('/search/data/vrqo_data/base/norm/vrqo_VRInfo')
    write_text(test_text, '/search/data/vrqo_data/base/norm/vrqo_VRInfo_for_text')
    modify_list = [
        {
            "anchor": ["^INTERNAL.GOUZAI.ANDBANG"],
            "action": "delete",
            "content": "for test_1"
        },
        {
            "anchor": ["^EXTERNAL.MAP.NMPLACE"],
            "action": "replace",
            "content": "for test_2"
        },
        {
            "anchor": ["^INTERNAL.NEWS.WEIBO"],
            "action": "append",
            "content": "for test_3"
        },
        {
            "anchor": ["^INTERNAL.barcode.pc"],
            "action": "insert",
            "content": "for test_4"
        }]
    modify_text(modify_list, '/search/data/vrqo_data/base/norm/vrqo_VRInfo')