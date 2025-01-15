import os
from pathlib import Path

import pytest

from base import Driver
from common import Excel, data_parse, LogUtils, Env, Config
from common import generate_execution_order


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # 检查环境变量
    Env().check_env()

    # 将pytest.ini中的log_file参数设置为绝对路径
    rootdir = config.rootdir
    default_log_file = "logs/pytest.log"
    log_file = config.getoption('--log-file') or config.getini('log_file') or default_log_file
    if hasattr(config.option, 'log_file'):
        config.option.log_file = str(rootdir / log_file)

    # 添加以session为单位的重复测试
    if hasattr(config.option, 'repeat_scope') and hasattr(config.option, 'count'):
        config.option.repeat_scope = 'session'
        config.option.count = 1

    # 添加测试函数依赖关系
    config.addinivalue_line(
        "markers",
        "dependency(name=None, depends=[]): mark a test to be used as a dependency for other tests or to depend on other tests."
    )


@pytest.fixture(scope="class", autouse=True)
def session_load():
    # 加载session
    Driver().sessionManger.load_session("login")


# 显式声明data
@pytest.fixture(scope="session")
def data(request):
    if hasattr(request, "param") and request.param:
        return request.param
    return None


def generate_order():
    dependency_config = Config.dependency_config()


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
            # indirect=True 表明data参数是通过fixture注入的，该数据直接传递到data fixture
            metafunc.parametrize("data", data, scope="function", indirect=True)


def pytest_collection_modifyitems(config, items):
    # 生成执行顺序列表
    execution_order = generate_execution_order()

    for item in items:
        item_fullpath = item.nodeid.split('[')[0].split('/')[1]
        order = execution_order.get(item_fullpath)
        item.add_marker(pytest.mark.run(order=order))


    # 数据链式依赖
    if hasattr(config.option, 'count') and config.option.count > 1:
        # 过滤测试项
        filtered_items = []
        for i, item in enumerate(items):
            # 获取当前测试项的重复轮次
            pytest_repeat_step_number = item.callspec.indices.get('__pytest_repeat_step_number')
            data_index = int(item.callspec.id.split('-')[0][-1])
            if data_index == pytest_repeat_step_number:
                filtered_items.append(item)
        # 替换原始测试项列表，并保留原有引用
        items[:] = filtered_items

    # 遍历所有测试项，动态添加依赖关系
    for item in items:
        # 获取测试函数的模块名、类名和函数名
        module_name = item.module.__name__ + '.py'
        class_name = item.cls.__name__ if item.cls else None
        func_name = item.originalname
        dependency_config = Config.dependency_config()
        node_id = {}
        suffix = f'[{item.callspec.id}]'

        # 检查是否有配置文件中的依赖关系
        if module_name in dependency_config:
            module_deps = dependency_config[module_name]
            if class_name and class_name in module_deps:
                class_deps = module_deps[class_name]
                if func_name in class_deps:
                    dep_info = class_deps[func_name]
                    node_id.update({dep_info.get('name', func_name): item.nodeid.split('[')[0]})
                    name = None
                    scope = dep_info.get('scope', 'session')
                    depends = []
                    if dep_info.get('depends'):
                        for dep in dep_info.get('depends'):
                            if dep in node_id:
                                depends.append(f'{node_id.get(dep)}')
                    # 动态添加 dependency marker
                    item.add_marker(
                        pytest.mark.dependency(
                            name=name,
                            scope=scope,
                            depends=depends
                        )
                    )


# 测试函数日志收集
@pytest.fixture(scope="function", autouse=True)
def test_log_collect(data, request):
    node_id = request.node.nodeid
    LogUtils().infos(f"node_id:{node_id}")
    LogUtils().infos("-------------------test start-------------------")
    LogUtils().infos(f"test data: {data}")
    yield
    LogUtils().infos("-------------------test end---------------------")
