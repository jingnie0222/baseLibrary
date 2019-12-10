import re


def trim_head_tail(content=''):
    if content != '':
        content = content.strip('\r\n')
        content = content.strip('\n')
        content = content.strip(' ')
        content = content.strip('\t')
    return content


def extract_data(content='', rule='', incise_begin=1, incise_stop=-1):
    data = ''
    if content != '' and rule != '':
        data_search = re.search(rule, content)
        if data_search is not None:
            data_group = data_search.group()
            if incise_stop == 0:
                data = data_group[incise_begin:]
            else:
                data = data_group[incise_begin:incise_stop]
    return data


# for test
if __name__ == "__main__":
    content_new = trim_head_tail('    hello word    \r\n')
    content_sub = extract_data('  UserLabel="sougou label" subtest=a', 'UserLabel="(.*?)"', 11)
