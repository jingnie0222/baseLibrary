import os
import sys


def gen_start_shell_from_sql(mysql_info, module_type):
    from lib.mysql_interaction import MYSQLClient
    is_ok = False
    mysql_client = MYSQLClient(mysql_info['mysql_user'], mysql_info['mysql_password'], mysql_info['mysql_ip'],
                               mysql_info['mysql_port'], mysql_info['mysql_database'])
    status, title, data = mysql_client.execute_sql(
        'select * from offline_module_config_info where module = "' + module_type + '"')
    if status and len(title) > 0 and len(data) == 1:
        start_shell = 'start_shell_' + module_type + '.sh'
        f_hd = open(os.path.join(sys.path[0], start_shell), 'w')
        f_hd.write(data[0][title.index('script')])
        f_hd.close()
        is_ok = True
    mysql_client.close()
    return is_ok


def gen_start_shell_vrqo_dailybuild(conf_name):
    start_shell_vrqo = 'start_shell_vrqo.sh'
    shell_content = ["export LD_LIBRARY_PATH=lib\n",
                     "export LD_PRELOAD=/usr/lib64/libjemalloc.so\n",
                     "ulimit -c unlimited\n",
                     "setsid bin/vrqo  conf/" + conf_name + " >bin/std.log  2>bin/err.log &\n\n"]
    try:
        f_hd = open(os.path.join(sys.path[0], start_shell_vrqo), 'w')
    except:
        return False
    f_hd.writelines(shell_content)
    f_hd.close()
    return True


def gen_start_shell_vrqo_local(conf_name):
    start_shell_vrqo = 'start_shell_vrqo.sh'
    shell_content = ["export LD_LIBRARY_PATH=lib\n",
                     "export LD_PRELOAD=/usr/lib64/libjemalloc.so\n",
                     "ulimit -c unlimited\n",
                     "setsid ./vrqo  ./" + conf_name + " >./std.log  2>./err.log &\n\n"]
    try:
        f_hd = open(os.path.join(sys.path[0], start_shell_vrqo), 'w')
    except:
        return False
    f_hd.writelines(shell_content)
    f_hd.close()
    return True
