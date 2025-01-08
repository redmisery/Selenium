import traceback

import mysql.connector
from mysql.connector import Error

from common import LogUtils


class MysqlConnector:

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.connection = None

    # 连接数据库
    def connect_data(self):
        try:
            connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
            if connection.is_connected():
                debug_log = 'Mysql Connected'
                LogUtils().debug(debug_log)
                self.connection = connection
        except Error as e:
            error_log = f'Error connecting to MySQL:{e} {traceback.format_exc()}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    # 根据测试函数名查询测试数据表，若不存在则报错
    def get_test_data(self, table_name):
        """
        :param table_name: 表名
        :return: 表数据: 数组
        """
        try:
            if self.connection:
                connection = self.connection
                cursor = connection.cursor()
                sql_order = f'select * from {table_name};'
                cursor.execute(sql_order)
                data = cursor.fetchall()
                if data:
                    debug_log = f'get {table_name} data'
                    LogUtils().debug(debug_log)
                    return data
                else:
                    error_log = f'{table_name} data is empty'
                    LogUtils().errors(error_log)
        except Error as e:
            error_log = f'Error getting {table_name} data:{e} {traceback.format_exc()}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    # 关闭数据库
    def close_data(self):
        if self.connection:
            self.connection.close()
