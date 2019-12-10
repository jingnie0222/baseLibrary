import os
from lib.sys_inter_act import exe_sys_cmd_get_echo
from lib.svn_proc import SVNClient
from lib.ini_proc import modify_ini
from lib.ini_proc import parse_ini
from lib.logger import write_log


def get_job_ini(server = '', path = '', local_path = '.'):
    exe_sys_cmd_get_echo('rsync -vazP ' + server + '::' + path + '/info/job.ini ' + local_path + '/')
    if os.path.exists(local_path + '/job.ini'):
        return True
    else:
        return False


def modify_job_ini(config_modify_list = list(), local_path = ''):
    is_ok = False
    if not os.path.exists(local_path + '/job.ini'):
        return is_ok
    for config_modify_item in config_modify_list:
        if config_modify_item['config_type'] == 'ini':
            is_ok = modify_ini(config_modify_item['modContent'], local_path + '/job.ini')
            if not is_ok:
                write_log("modify ini file failed.  " + local_path + '/job.ini')
    return is_ok


def svn_get_package(job_ini = '', local_path = '', svn_user = '', svn_passwd = ''):
    if svn_user != '' and svn_passwd != '':
        svn_client = SVNClient(svn_user, svn_passwd)
    else:
        svn_client = SVNClient()
    job_ini_dict = parse_ini(job_ini)
    version_tag = ''
    if job_ini_dict.get('main.svn') is not None:
        for folder in job_ini_dict['main.svn'].keys():
            svn_client.svn_checkout(job_ini_dict['main.svn'][folder],
                                    os.path.join(local_path, folder))
            if folder == '.':
                version_tag = job_ini_dict['main.svn'][folder].split('/')[-1]
    return version_tag
