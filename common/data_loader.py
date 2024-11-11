import traceback
from pathlib import Path

import pandas
from pandas import DataFrame
from ruamel.yaml import YAML

from common import Config, LogUtils


class Excel:
    """
    Excel类
    """

    def __init__(self, path: Path):
        if path.exists():
            self.path = path
        else:
            error_log = f"{path} Excel file does not exist"
            LogUtils().error(error_log)
            raise error_log

    def read(self, sheet=0) -> list:
        """
        读取excel表
        :param sheet: sheet_name
        :return: dict
        """
        df = DataFrame(pandas.read_excel(self.path, sheet_name=sheet))
        # 判断excel表是否为空或数据为空
        if df.empty or df.isnull().all().all():
            error_log = f"{self.path} Excel file is empty"
            LogUtils().error(error_log)
            raise ValueError(error_log)
        else:
            data = df.applymap(lambda x: None if pandas.isna(x) else x).to_dict(orient='records')
            debug_log = "Read Excel file successfully"
            LogUtils().debug(debug_log)
            return data


class PublicData:
    """
    公共变量
    """
    yaml = YAML()
    public_data_path = Config().public_data_path

    @staticmethod
    def get(key, is_clear=False):
        """
        取出公共变量
        :param key: key
        :param is_clear: 是否清除{key: value}
        :return: value
        """
        with open(PublicData.public_data_path, encoding='utf-8', mode='r') as f:
            try:
                data = PublicData.yaml.load(f)
                value = data[key]
                if is_clear:
                    data.pop(key)
                    # 清除重写
                    f.truncate(0)
                    f.seek(0)
                    PublicData.yaml.dump(data, f)
                debug_log = f'get key: {key},value: {value}'
                LogUtils().debug(debug_log)
                return value
            except Exception as e:
                error_log = f'get key: {key} error,reason:{e},{traceback.format_exc()}'
                LogUtils().error(error_log)

    @staticmethod
    def put(key, value):
        """
        放置公共变量
        :param key:
        :param value:
        :return: 无
        """
        with open(PublicData.public_data_path, encoding='utf-8', mode='r+') as f:
            try:
                data = PublicData.yaml.load(f)
                if data is None:
                    data = {key: value}
                else:
                    data[key] = value
                f.truncate(0)
                f.seek(0)
                PublicData.yaml.dump(data, f)
                debug_log = f'put key: {key},value: {value}'
                LogUtils().debug(debug_log)
            except Exception as e:
                error_log = f'put key: {key},value: {value} error,reason:{e},{traceback.format_exc()}'
                LogUtils().error(error_log)

    @staticmethod
    def get_constant_data():
        """
        获取常量数据
        :return: dict
        """
        return PublicData.get('constant')


def DataParse(data: list) -> list:
    """
    解析字符串的{{key}}全局变量并根据value从data/constant_data.yaml获取value，替换{{key}}
    """
    constant_data = PublicData.get_constant_data()
    for i in data:
        for key, value in i.items():
            for k, v in constant_data.items():
                pattern = f"{{{{{k}}}}}"
                if pattern in str(value):
                    try:
                        value = value.replace(f"{{{{{k}}}}}", v)
                        i[key] = value
                        debug_log = f"{value} replace {k} to {v}"
                        LogUtils().debug(debug_log)
                    except Exception as e:
                        error_log = f'replace {k} to {v} faild!:{e}:{traceback.format_exc()}'
                        LogUtils().error(error_log)
    return data
