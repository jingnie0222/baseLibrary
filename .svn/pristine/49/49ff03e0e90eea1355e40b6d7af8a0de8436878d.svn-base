import os
import sys
import json
from lib.logger import write_log


def parse_json(json_file = './file.json'):
    json_dict = dict()
    if os.path.exists(json_file) and os.path.splitext(json_file)[1] == '.json':
        f_hd = open(json_file, 'r')
        try:
            json_dict = json.load(f_hd)
        except:
            json_dict.clear()
            write_log("failed. parse json file error, please check " + json_file)
        f_hd.close()
    else:
        write_log("failed. non-existent or non-json-format , please check " + json_file)
        #sys.exit(1)
    return json_dict


def write_json(data = dict(), json_file = './file.json'):
    try:
        f_hd = open(json_file, 'w')
    except:
        return False
    try:
        json.dump(data, f_hd, indent=4)
    except:
        f_hd.close()
        return False
    f_hd.close()
    return True

