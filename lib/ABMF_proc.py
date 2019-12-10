import os
import time
import re
from collections import defaultdict
from lib.logger import write_log
from lib.sys_inter_act import exe_sys_cmd_get_echo
from lib.common_function import trim_head_tail

# ABMF:  angle brackets marked file


def _tree():
    return defaultdict(_tree)


def parse_QO_config(ABMF_file, split_point):
    ABMF_list = list()
    ABMF_partial_fragment = _tree()
    if not os.path.exists(ABMF_file):
        write_log("failed. non-existent, please check " + ABMF_file)
        return ABMF_list, ABMF_partial_fragment
    f_hd = open(ABMF_file, 'r')
    if len(split_point) == 0:
        ABMF_list = f_hd.readlines()
        f_hd.close()
        return ABMF_list, ABMF_partial_fragment
    is_find = False
    sub_content = ''
    sub_key = ''
    split_point_index = 0
    for line in f_hd:
        # hard code for vrqo_QOConfig modification
        if line.find('# rule : map.index blk') != -1:
            ABMF_list.append('#---divide_line---\n')
        if not is_find:
            for check_point in split_point:
                if line.find(check_point["start"]) != -1:
                    sub_content = line
                    is_find = True
                    break
                split_point_index += 1
            if is_find:
                continue
            else:
                split_point_index = 0
        if is_find:
            if line.find(split_point[split_point_index]["end"]) != -1:
                sub_content = sub_content + line
                ABMF_partial_fragment[split_point[split_point_index]["start"]][sub_key] = sub_content
                ABMF_list.append('PlaceHolder__' + '--'.join([split_point[split_point_index]["start"], sub_key]))
                split_point_index = 0
                is_find = False
            if not is_find:
                continue
        if is_find:
            sub_content = sub_content + line
            if line.find(split_point[split_point_index]["key"]) != -1:
                sub_key = trim_head_tail(line.split('=')[1])
            continue
        ABMF_list.append(line)
    f_hd.close()
    return ABMF_list, ABMF_partial_fragment


def write_QO_config(ABMF_list, ABMF_partial_fragment, ABMF_file = './file.ABMF'):
    if len(ABMF_list) == 0:
        return False
    try:
        f_hd = open(ABMF_file, 'w')
    except:
        return False
    if len(ABMF_partial_fragment) == 0:
        f_hd.writelines(ABMF_list)
        f_hd.close()
        return True
    divide_line = 0
    for index in range(len(ABMF_list)):
        # hard code for vrqo_QOConfig modification
        if trim_head_tail(ABMF_list[index]) == '#---divide_line---':
            divide_line = index
        if re.search('^PlaceHolder__', ABMF_list[index]) is None:
            continue
        key_list = ABMF_list[index][len('PlaceHolder__'):].split('--')
        if len(key_list) != 2:
            ABMF_list[index] = '\n'
            continue
        if len(ABMF_partial_fragment[key_list[0]][key_list[1]]) > 0:
            ABMF_list[index] = ABMF_partial_fragment[key_list[0]][key_list[1]]
        else:
            ABMF_list[index] = '\n'
            continue
        ABMF_partial_fragment[key_list[0]].pop(key_list[1])
    #hard code for vrqo_QOConfig modification
    for key in ABMF_partial_fragment['<PATTERN NEW>'].keys():
        if len(ABMF_partial_fragment['<PATTERN NEW>'][key]) > 0:
            ABMF_list[divide_line] = ABMF_partial_fragment['<PATTERN NEW>'][key] + ABMF_list[divide_line]
    for key in ABMF_partial_fragment['<RULE NEW>'].keys():
        if len(ABMF_partial_fragment['<RULE NEW>'][key]) > 0:
            ABMF_list.append(ABMF_partial_fragment['<RULE NEW>'][key])
    f_hd.writelines(ABMF_list)
    f_hd.close()
    return True


def merge_QO_config_fragment(ABMF_partial_fragment_s, ABMF_partial_fragment_d, merge_key_list):
    for key_1 in merge_key_list.keys():
        for key_2 in merge_key_list[key_1]:
            if (ABMF_partial_fragment_s.get(key_1) is not None) and (
                    ABMF_partial_fragment_s[key_1].get(key_2) is not None):
                if ABMF_partial_fragment_d.get(key_1) is not None:
                    ABMF_partial_fragment_d[key_1][key_2] = ABMF_partial_fragment_s[key_1][key_2]
                else:
                    ABMF_partial_fragment_d[key_1] = {key_2:ABMF_partial_fragment_s[key_1][key_2]}


def merge_QO_config(ABMF_file_s, ABMF_file_d, split_point, merge_key_list):
    QO_config_s_main, QO_config_s_fragment = parse_QO_config(ABMF_file_s, split_point)
    QO_config_d_main, QO_config_d_fragment = parse_QO_config(ABMF_file_d, split_point)
    merge_QO_config_fragment(QO_config_s_fragment, QO_config_d_fragment, merge_key_list)
    exe_sys_cmd_get_echo('cp -f ' + ABMF_file_d + ' ' + ABMF_file_d + '_bak_' + str(int(time.time())))
    write_QO_config(QO_config_d_main, QO_config_d_fragment, ABMF_file_d)


# for test
if __name__ == "__main__":
    #step by step debugging
    QO_config_s_main, QO_config_s_fragment = parse_QO_config('/search/data/vrqo_data/base/norm/vrqo_QOConfig_pre-online',
                                                             [{"start": "<PATTERN NEW>", "end": "<PATTERN END>",
                                                               "key": "PATTERN_NAME"},
                                                              {"start": "<RULE NEW>", "end": "<RULE END>",
                                                               "key": "RULE_NAME"}])
    QO_config_d_main, QO_config_d_fragment = parse_QO_config('/search/data/vrqo_data/base/norm/vrqo_QOConfig',
                                                             [{"start": "<PATTERN NEW>", "end": "<PATTERN END>",
                                                               "key": "PATTERN_NAME"},
                                                              {"start": "<RULE NEW>", "end": "<RULE END>",
                                                               "key": "RULE_NAME"}])
    merge_QO_config_fragment(QO_config_s_fragment, QO_config_d_fragment,
                     {'<PATTERN NEW>': ['70009639_PKEY_PATTERN', '70009639_BLK.SUB_PATTERN'],
                      '<RULE NEW>': ['70119638_WORDLIST_RULE', '70009638_BLK_RULE']})
    write_QO_config(QO_config_d_main, QO_config_d_fragment, '/search/data/vrqo_data/base/norm/vrqo_QOConfig')

    #Overall call
    merge_QO_config('/search/data/vrqo_data/base/norm/vrqo_QOConfig_pre-online',
                     '/search/data/vrqo_data/base/norm/vrqo_QOConfig',
                     [{"start": "<PATTERN NEW>", "end": "<PATTERN END>",
                       "key": "PATTERN_NAME"},
                      {"start": "<RULE NEW>", "end": "<RULE END>",
                       "key": "RULE_NAME"}],
                     {'<PATTERN NEW>': ['70009639_PKEY_PATTERN', '70009639_BLK.SUB_PATTERN'],
                      '<RULE NEW>': ['70119638_WORDLIST_RULE', '70009638_BLK_RULE']}
                     )
