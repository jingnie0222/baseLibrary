import os
import re
import subprocess
import time
from lib.common_function import trim_head_tail
from lib.logger import write_log
from lib.timer_mgmt import CountdownTimer
from lib.timer_mgmt import time_sleep


def exe_sys_cmd_get_echo(os_cmd = ''):
    cmd_echo = ''
    if os_cmd != '':
        write_log(os_cmd)
        cmd_pipe = os.popen(os_cmd)
        cmd_echo = cmd_pipe.read()
        cmd_pipe.close()
        write_log(cmd_echo)
    return cmd_echo


def exe_sys_cmd(os_cmd = ''):
    if os_cmd != '':
        write_log(os_cmd)
        os.system(os_cmd)
    return


def exe_sys_cmd_get_echo_v3(os_cmd = ''):
    # need python3
    cmd_echo = ''
    echo_error_code = -1
    if os_cmd != '':
        write_log(os_cmd)
        echo_error_code, cmd_echo = subprocess.getstatusoutput(os_cmd)
        write_log(cmd_echo)
    return cmd_echo, echo_error_code


def exe_sys_cmd_v3(os_cmd = ''):
    # need python3
    is_ok = False
    if os_cmd != '':
        write_log(os_cmd)
        echo_error_code = subprocess.call(os_cmd, shell=True)
        if echo_error_code == 0:
            is_ok = True
    return is_ok


def split_sys_cmd_echo(os_cmd_echo = '', position = -1, echo_line_split_len = 0):
    os_cmd_echo_split = list()
    os_cmd_echo = trim_head_tail(os_cmd_echo)
    if os_cmd_echo == '':
        return os_cmd_echo_split
    echo_line_len = 0
    for echo_line in os_cmd_echo.split('\n'):
        echo_line_split = re.split('\s+|\t+', echo_line)
        if echo_line_len < len(echo_line_split):
            echo_line_len = len(echo_line_split)
        os_cmd_echo_split.append(echo_line_split)
    if echo_line_split_len > 0:
        echo_line_len = echo_line_split_len
    for index in range(len(os_cmd_echo_split) - 1, -1, -1):
        if len(os_cmd_echo_split[index]) < echo_line_len:
            os_cmd_echo_split.pop(index)
    if 0 <= position < echo_line_len:
        os_cmd_echo_split_partial = list()
        for it in os_cmd_echo_split:
            os_cmd_echo_split_partial.append(it[position])
        return os_cmd_echo_split_partial
    else:
        return os_cmd_echo_split


def get_service_pid(service_name = ''):
    pid_list = []
    if service_name != '':
        cmd_echo = exe_sys_cmd_get_echo('ps -ef | grep  ' + service_name + ' | grep -v grep | grep -v "You have new mail in"')
        if cmd_echo != '':
            pid_list = split_sys_cmd_echo(cmd_echo, 1, 8)
    return pid_list


def get_service_path_by_pid(pid_list = []):
    pid_path_dict = dict()
    for pid in pid_list:
        pid_path_dict[pid] = ''
        cmd_echo = exe_sys_cmd_get_echo('pwdx  ' + pid)
        if cmd_echo.find('No such process') != '':
            for it in cmd_echo.split('\n'):
                if it.find(pid) != -1:
                    pid_path_dict[pid] = trim_head_tail(it.split(':')[1])
    return pid_path_dict


def monitor_port_by_pid(pid = '0', listen_port = '0'):
    is_ok = False
    if int(listen_port) > 0:
        cmd_echo = exe_sys_cmd_get_echo('netstat -nlp | grep :' + listen_port)
        if cmd_echo.find(' ' + pid + '/') != -1:
            is_ok = True
    else:
        cmd_echo = exe_sys_cmd_get_echo('netstat -nlp | grep ' + pid)
        if re.search('LISTEN\s+' + pid + '/', cmd_echo) is not None:
            is_ok = True
    return is_ok


def start_service(service_name = '', service_path = '', start_script = '', listen_port = '0', time_out = 0):
    start_time = time.time()
    start_time_cost = 0.0
    is_ok = False
    service_pid = '0'
    if os.path.exists(start_script.split(' ')[0]):
        exe_sys_cmd('dos2unix ' + start_script.split(' ')[0])
        start_script_path = os.path.abspath(os.path.dirname(start_script))
        start_script_name = os.path.basename(start_script)
        if os.path.exists(start_script_path):
            current_path = os.getcwd()
            os.chdir(start_script_path)
            exe_sys_cmd('chmod +x ' + start_script_name.split(' ')[0])
            if exe_sys_cmd_get_echo_v3('./' + start_script_name)[1] == 0:
                time_sleep(3)
                pid_list = get_service_pid(service_name)
                pid_path_dict = get_service_path_by_pid(pid_list)
                for pid in pid_path_dict.keys():
                    if pid_path_dict[pid] == os.path.abspath(service_path + '/'):
                        service_pid = pid
                        break
                if int(service_pid) > 0:
                    timer = CountdownTimer(time_out)
                    timer.start()
                    while timer.isAlive():
                        if monitor_port_by_pid(pid, listen_port):
                            is_ok = True
                            timer.stop()
            os.chdir(current_path)
    if is_ok:
        start_time_cost = time.time() - start_time
    return is_ok, service_pid, start_time_cost


def stop_service(service_pid = '0', time_out = 0):
    is_ok = True
    if not os.path.exists('/proc/' + service_pid):
        return is_ok
    is_ok = False
    attempts = 3
    time_out_slot = int(time_out/4)
    for attempt_id in range(attempts):
        exe_sys_cmd('kill ' + service_pid)
        timer = CountdownTimer(time_out_slot)
        timer.start()
        while timer.isAlive():
            if not os.path.exists('/proc/' + service_pid):
                is_ok = True
                timer.stop()
        if is_ok:
            break
    if is_ok and (not os.path.exists('/proc/' + service_pid)):
        return is_ok
    exe_sys_cmd('kill -9 ' + service_pid)
    time_sleep(time_out_slot)
    if os.path.exists('/proc/' + service_pid):
        is_ok = False
    else:
        is_ok = True
    return is_ok


def stop_all_service_forcibly(service_name = '', time_out = 0):
    is_ok = False
    exe_sys_cmd('pkill -9 -f ' + service_name)
    time_sleep(time_out)
    cmd_echo = exe_sys_cmd_get_echo(
        'ps -ef | grep  ' + service_name + ' | grep -v grep | grep -v "You have new mail in"')
    if cmd_echo.find(service_name) == -1:
        is_ok = True
    return is_ok


def check_is_local_server(ip = ''):
    if exe_sys_cmd_get_echo('ifconfig -a |grep ' + ip).find(ip) != -1:
        return True
    else:
        return False


# for test
if __name__ == "__main__":
    exe_sys_cmd("ls -rtl ")
    echo = exe_sys_cmd_get_echo("ls -rtl ")
    echo_split_to_list = split_sys_cmd_echo(echo)
    echo_split_to_list_partial = split_sys_cmd_echo(echo, 5)

    is_ok = stop_all_service_forcibly('lt-vrqo', 30)
    is_ok, pid, cost = start_service('lt-vrqo',
                                     '/search/odin/xujiang/vrqo_online/QueryOptimizer',
                                     '/search/odin/xujiang/vrqo_online/QueryOptimizer/start_vrqo.sh func',
                                     '8033', 360)
    is_ok = stop_service(pid, 120)
