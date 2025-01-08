import os
from pathlib import Path

import pytest

from base import Driver
from common import Excel, data_parse, LogUtils, Env


# 环境变量加载
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart():
    Env().check_env()

# session会话加载
@pytest.fixture(scope="class", autouse=True)
def session_log_collect():
    Driver().sessionManger.load_session("login")

# 显式声明data
@pytest.fixture(scope="session")
def data(request):
    if hasattr(request, "param") and request.param:
        return request.param
    return None


# 钩子函数对data参数化
def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        # 获取函数名
        function_name = metafunc.function.__name__
        # 获取数据文件名
        data_file = Path(metafunc.module.__file__).name.split(".")[0] + ".xlsx"
        data_file_path = Path(os.getenv("DATA_PATH")) / data_file
        # 读取数据
        excel_data = Excel(data_file_path).read(function_name)
        # 解析数据
        if excel_data:
            data = data_parse(excel_data)
            metafunc.parametrize("data", data, scope="function", indirect=True)


@pytest.fixture(scope='session')
def test_id():
    """
    测试用例ID生成器
    """
    pre_function_name = None
    function_id = 0
    data_id = 0

    def generate_id(function_name):
        # 闭包变量
        nonlocal pre_function_name, function_id, data_id
        if pre_function_name is None or pre_function_name != function_name:
            function_id += 1
            data_id = 1
            pre_function_name = function_name
        else:
            data_id += 1
        return f"{function_name}_{function_id}_{data_id}"

    return generate_id


# 测试函数日志收集
@pytest.fixture(scope="function", autouse=True)
def test_log_collect(data, test_id, request):
    generate_test_id = test_id
    LogUtils().infos(f"test_id:{generate_test_id(request.function.__name__)}")
    LogUtils().infos("-------------------test start-------------------")
    LogUtils().infos(f"test data: {data}")
    yield
    LogUtils().infos("-------------------test end---------------------")