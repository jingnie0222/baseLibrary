import os
from lib.sys_inter_act import exe_sys_cmd_v3, exe_sys_cmd_get_echo
from lib.yum_proc import yum_install_referto_jobini


def compile_cplus(build_path):
    build_succ = False
    if os.path.exists(build_path):
        current_path = os.getcwd()
        os.chdir(build_path)
        # build_succ = exe_sys_cmd_v3('autoreconf -isv && ./configure  && make -j')
        build_succ = exe_sys_cmd_v3('make -j')
        os.chdir(current_path)
    return build_succ


def compile_dailybuild(job_ini = '', local_path = ''):
    dailybuild_file = ''
    exe_sys_cmd_get_echo('rm -f  ' + local_path + '/_result_/result.tar.gz')
    if not yum_install_referto_jobini(job_ini, 'local'):
        return False, dailybuild_file
    exe_sys_cmd_get_echo('sgbuild -i docker-reg.sogou-inc.com/sgbuild/centos7.4:6 -c ' + job_ini + ' -d ' + local_path)
    if os.path.exists(local_path + '/_result_/result.tar.gz'):
        if os.path.exists(local_path + '/_result_/result.tar.gz'):
            exe_sys_cmd_get_echo('rm -rf  ' + local_path + '/dailybuild/')
            exe_sys_cmd_get_echo('mkdir -p ' + local_path + '/dailybuild/')
            exe_sys_cmd_get_echo('tar -xf ' + local_path + '/_result_/result.tar.gz -C ' + local_path + '/dailybuild/')
            exe_sys_cmd_get_echo('mv ' + local_path + '/dailybuild/opt/sogou/lib64  ' + local_path + '/dailybuild/opt/sogou/lib')
            # add modified conf files in daily build
            exe_sys_cmd_get_echo('cp -rf ' + local_path + '/conf  ' + local_path + '/dailybuild/opt/sogou/')
            exe_sys_cmd_get_echo('tar -czf ' + local_path + '/dailybuild/dailybuild.tar.gz  -C ' + local_path + '/  dailybuild/opt')
            if os.path.exists(local_path + '/dailybuild/dailybuild.tar.gz'):
                dailybuild_file = local_path + '/dailybuild/dailybuild.tar.gz'
                return True, dailybuild_file
    return False, dailybuild_file
