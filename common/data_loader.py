import os
import traceback
from pathlib import Path
from typing import Union, Optional

import pandas
from pandas import DataFrame
from ruamel.yaml import YAML

from common import LogUtils


class Excel:
    """
    Excel类
    """

    def __init__(self, path: Path):
        if path.exists():
            self.path = path
        else:
            self.path = None
            error_log = f"{path} Excel file does not exist"
            LogUtils().errors(error_log)

    def read(self, sheet: Union[str, int, None] = 0) -> Optional[list[dict]]:
        """
        读取excel表
        :param sheet: sheet_name
        :return: dict
        """
        if sheet is None or self.path is None:
            debug_info = f"Read {self.path} file failed, sheet or path is None"
            LogUtils().debug(debug_info)
            return None

        try:
            df = DataFrame(pandas.read_excel(self.path, sheet_name=sheet))
        except Exception as e:
            error_log = f"Read {self.path}.{sheet} file failed,reason:{e},{traceback.format_exc()}"
            LogUtils().errors(error_log)
            return None
        # 判断excel表是否为空或数据为空
        if df.empty or df.isnull().all().all():
            error_log = f"{self.path} Excel file is empty"
            LogUtils().errors(error_log)
            return None
        else:
            # 转换为字典，并将空值替换为None
            data = df.where(pandas.notna(df), None).to_dict(orient='records')
            debug_log = f"Read {self.path} file successfully"
            LogUtils().debug(debug_log)
            return data


class PublicData:
    """
    公共变量
    """
    yaml = YAML()

    @staticmethod
    def get(key, is_clear=False):
        """
        取出公共变量
        :param key: key
        :param is_clear: 是否清除{key: value}
        :return: value
        """
        with open(os.getenv("PUBLIC_DATA_PATH"), encoding='utf-8', mode='r') as f:
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
                LogUtils().errors(error_log)

    @staticmethod
    def put(key, value):
        """
        放置公共变量
        :param key:
        :param value:
        :return: 无
        """
        with open(os.getenv("PUBLIC_DATA_PATH"), encoding='utf-8', mode='r+') as f:
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
                LogUtils().errors(error_log)

    @staticmethod
    def get_constant_data():
        """
        获取常量数据
        :return: dict
        """
        return PublicData.get('constant')


def data_parse(data: list) -> list:
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
                    except Exception as e:
                        error_log = f'replace {k} to {v} failed!:{e}:{traceback.format_exc()}'
                        LogUtils().errors(error_log)
    return data
