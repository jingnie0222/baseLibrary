import pymysql
from lib.logger import write_log


def mysql_alive(func):
    def wrapper(self, *args, **kwargs):
        if self.mysql_is_alive:
            return func(self, *args, **kwargs)
    return wrapper


class MYSQLClient():
    def __init__(self, user, password, ip, port, database):
        self.mysql_is_alive = False
        try:
            self.mysql_conn = pymysql.connect(user=user, password=password, host=ip, port=int(port), database=database)
            self.mysql_is_alive = True
        except Exception as err:
            write_log(err)

    @mysql_alive
    def close(self):
        self.mysql_conn.close()

    @mysql_alive
    def execute_sql(self, command = '', database = ''):
        is_ok = True
        table_head_list = list()
        data_list = list()
        try:
            cursor = self.mysql_conn.cursor()
            if database != '':
                cursor.execute('use ' + database)
            rowcount = cursor.execute(command)
            if rowcount > 0:
                if cursor.description is not None:
                    table_head_list = [tuple[0] for tuple in cursor.description]
                    for data in cursor.fetchall():
                        if len(table_head_list) == len(data):
                            data_list.append(list(data))
                        else:
                            is_ok = False
                            table_head_list.clear()
                            data_list.clear()
                            break
            self.mysql_conn.commit()
            cursor.close()
        except Exception as err:
            is_ok = False
            table_head_list.clear()
            data_list.clear()
            write_log(command)
            write_log(err)
        return is_ok, table_head_list, data_list


# for test
if __name__ == "__main__":
    mysql_client = MYSQLClient('main_project', 'main_project', '10.134.104.40', 3306, 'main_project')
    status, title, data = mysql_client.execute_sql('select * from django_migrations')
    # status, title, data = mysql_client.execute_sql("INSERT INTO offline_env_info VALUES (3,'test3',3234,'add','key3')")
    mysql_client.close()
    print('status', status)
    print('title', title)
    print('data', data)
