from pathlib import Path

import pytest

from common import Excel, DataParse, Config, LogUtils


# 钩子函数添加data参数
def pytest_addoption(parser):
    parser.addoption("--data", action="append", default=[], help="data transport")


# 钩子函数对data参数化
def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        # 获取函数名
        function_name = metafunc.function.__name__
        # 获取数据文件名
        data_file = Path(metafunc.module.__file__).name.split(".")[0] + ".xlsx"
        data_file_path = Config().data_path / data_file
        # 读取数据
        excel_data = Excel(data_file_path).read(function_name)
        # 解析数据
        data = DataParse(excel_data)
        metafunc.parametrize("data", data, scope="function")


# 测试函数日志收集
@pytest.fixture(autouse=True, scope="function")
def test_collect(data):
    LogUtils().info("-------------------test start-------------------")
    LogUtils().info(f"test data: {data}")
    yield
    LogUtils().info("-------------------test end-------------------")
