import os
from lib.sys_inter_act import exe_sys_cmd_get_echo


class SVNClient:
    def __init__(self, username='qa_svnreader', password='New$oGou4U!'):
        self.username = username
        self.password = password

    def svn_checkout(self, svn_url, local_path):
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        exe_sys_cmd_get_echo("svn --username '" + self.username + "' --password '" + self.password + "'  checkout " +
                             svn_url + " " +
                             local_path)


# for test
if __name__ == "__main__":
    SVNClient('qa_svnreader', 'New$oGou4U!').svn_checkout(
        'http://svn.sogou-inc.com/svn/websearch4/VH/openhub_new/branches/2019.10.28-annotation_brackets_test',
        '/search/odin/xujiang/test/openhub_test')
