import os
import traceback
from collections import namedtuple, defaultdict
from pathlib import Path
from typing import Union, Optional, Any, Dict

import pandas
from dotenv import load_dotenv
from pandas import DataFrame
from ruamel.yaml import YAML

from common.log import LogUtils


class Excel:
    """
    Excel类
    处理Excel类型的测试数据
    """

    @staticmethod
    def _process_dataframe(path, df: DataFrame) -> Optional[list[dict]]:
        """
            处理 DataFrame，转换为字典列表
            :param df: 输入的 DataFrame
            :return: 字典列表，如果 DataFrame 为空则返回 None
            """
        if df.empty or df.isnull().all().all():
            error_log = f"{path} Excel file is empty"
            LogUtils().errors(error_log)
            return None
        else:
            # 转换为字典，并将空值替换为None
            data = df.where(pandas.notna(df), None).to_dict(orient='records')
            return data

    @classmethod
    def read(cls, path, sheet: Union[str, int, None] = None) -> None | dict[Any, list[dict] | None] | list[dict]:
        """
        读取excel表
        :param path: 文件路径
        :param sheet: sheet_name，默认是None，返回所有sheet数据
        :return: dict
        """
        path = Path(path)
        if not path.exists():
            debug_info = f"Read {path} file failed, sheet or path is None"
            LogUtils().debug(debug_info)
            return None

        try:
            if sheet is None:
                all_sheets = pandas.read_excel(path, sheet_name=sheet)
                data = {sheet_name: cls._process_dataframe(path, df)
                        for sheet_name, df in all_sheets.items()}
            else:
                df = pandas.read_excel(path, sheet_name=sheet)
                data = cls._process_dataframe(path, df)
            debug_log = f"Read {path} file successfully"
            LogUtils().debug(debug_log)
            return data
        except Exception as e:
            error_log = f"Read {path}.{sheet} file failed,reason:{e},{traceback.format_exc()}"
            LogUtils().errors(error_log)
            return None

    @classmethod
    def get_all_testdata(cls):
        """
        获取所有测试数据
        """
        data_dir = Path(os.getenv("DATA_PATH"))
        data = {}
        if data_dir.exists():
            data_files = data_dir.glob("*.xlsx")
            for file in data_files:
                # key为对应测试文件名，value为测试数据
                data[file.stem+'.py'] = cls.read(file)
        return data

    @classmethod
    def testdata_length_parse(cls, data: Dict[str, Dict[str, list]]):
        """
        解析测试数据长度
        """
        data_length = defaultdict(dict)
        for filename, fun_data in data.items():
            for fun_name, value in fun_data.items():
                cur_length = len(value)
                data_length[filename][fun_name] = cur_length
        return data_length

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

    @staticmethod
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

if __name__ == '__main__':
    # 测试代码
    load_dotenv(r'C:\Users\hanyan\PycharmProjects\Selenium\env\.env')
    data = Excel.get_all_testdata()
    data_length = Excel.testdata_length_parse(data)
    print(data)
    print(data_length)
    print(data_length['1'])