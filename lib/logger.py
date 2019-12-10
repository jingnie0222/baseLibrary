import os
import sys
import time
import logging


def write_log(log_content, log_file='sys.log', log_oper_mode='a'):
    if isinstance(log_content, str):
        str_log_content = log_content
    else:
        str_log_content = str(log_content)
    log_file_path, log_file_name = os.path.split(log_file)
    if log_file_path == '':
        log_file_path = sys.path[0] + '/log/'
        log_file = os.path.join(log_file_path, log_file_name)
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    if str_log_content != '':
        print(str_log_content)
        file_handle = open(log_file, log_oper_mode)
        file_handle.write("[" + time.ctime() + "]  " + str_log_content)
        file_handle.write('\n')
        file_handle.close()
    return None


def create_logger(log_name = 'system',
        log_path = sys.path[0] + '/log/',
        log_level = 'INFO',
        log_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'):
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logger = logging.getLogger(log_name)
    if not logger.handlers:
        logger.setLevel(logging._nameToLevel[log_level])
        log_hander = logging.FileHandler(os.path.join(log_path, log_name + '.log'))
        log_hander.setFormatter(logging.Formatter(log_format))
        logger.addHandler(log_hander)
    return logger
