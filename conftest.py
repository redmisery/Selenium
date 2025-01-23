from collections import defaultdict
from pathlib import Path

import pytest

from base import Driver
from common import Excel, LogUtils, Env, Config, PublicData
from common import generate_execution_order

all_test_data: [dict] = {}
data_length: [defaultdict] = {}
order_fullpath = generate_execution_order()


def pytest_addoption(parser):
    # 注册自定义配置项
    parser.addini("data_sources", help="Specify the data sources for tests", default="excel")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    global all_test_data
    global data_length
    # 检查环境变量
    Env().check_env()

    # 将pytest.ini中的log_file参数设置为绝对路径
    rootdir = config.rootdir
    default_log_file = "logs/pytest.log"
    log_file = config.getoption('--log-file') or config.getini('log_file') or default_log_file
    if hasattr(config.option, 'log_file'):
        config.option.log_file = str(rootdir / log_file)

    # 加载所有测试数据
    if config.getini('data_sources') == 'excel':
        all_test_data = Excel.get_all_testdata()
        data_length = Excel.testdata_length_parse(all_test_data)

    # 该配置打开时，依赖关系为函数全路径
    function_dependency_mode = Config.getini('data', 'function_dependency_mode', bool)
    # 该配置打开时，数据链式依赖为每个测试用例添加数据索引后缀
    data_chain_dependency_mode = Config.getini('data', 'data_chain_dependency_mode', bool)

    # 添加以session为单位的重复测试
    if function_dependency_mode:
        # 无需任何操作
        pass
    if data_chain_dependency_mode and hasattr(config.option, 'repeat_scope') and hasattr(config.option, 'count'):
        config.option.repeat_scope = 'session'
        execute_order = order_fullpath.order
        # 计算重复次数,次数取决于第一个测试用例的执行次数
        filename, _, func_name = execute_order.inverse[1].split('::')
        config.option.count = data_length[filename][func_name]

    # 添加测试函数依赖关系
    config.addinivalue_line(
        "markers",
        "dependency(name=None, depends=[]): mark a test to be used as a dependency for other tests or to depend on other tests."
    )


# 显式声明data
@pytest.fixture(scope="session")
def data(request):
    param = request.param if hasattr(request, "param") and request.param else None
    return param


# 钩子函数对data参数化
def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        # 获取函数名
        function_name = metafunc.function.__name__
        # 获取数据文件名
        test_filename = Path(metafunc.module.__file__).name
        # 读取数据
        global all_test_data
        try:
            excel_data = all_test_data[test_filename][function_name]
        except KeyError as e:
            error_log = f"未找到测试数据文件{test_filename}中{function_name}的测试数据"
            LogUtils().error(error_log)
            raise Exception(error_log) from e
        # 解析数据
        data = PublicData.data_parse(excel_data)
        # indirect=True 表明data参数是通过fixture注入的，该数据直接传递到data fixture
        metafunc.parametrize("data", data, scope="function", indirect=True)


def pytest_collection_modifyitems(config, items):
    # 生成执行顺序列表
    global order_fullpath
    global data_length
    execute_order = order_fullpath.order
    name_to_fullpath = order_fullpath.name_to_fullpath
    session_loop = config.option.count if hasattr(config.option, 'count') else 1

    # 获取配置
    data_chain_dependency_mode = Config.getini('data', 'data_chain_dependency_mode', bool)

    # 添加测试用例执行顺序,注意，排序超过10000时，排序将失效，只适用于小于10000的排序
    for item in items:
        item_fullpath = item.nodeid.split('[')[0].split('/')[1]
        item_loop = item.callspec.indices.get('__pytest_repeat_step_number', 0)
        order = execute_order.get(item_fullpath)
        item.add_marker(pytest.mark.run(order=order + item_loop * 10000))

    # 数据链式依赖,以下为过滤规则：每一轮session重复测试只有一组数据，且数据按照顺序执行
    if data_chain_dependency_mode and hasattr(config.option, 'count') and config.option.count > 1:
        # 过滤测试数据，保证每一个session重复测试只有一组数据，且数据按照顺序执行
        filtered_items = []
        for i, item in enumerate(items):
            item_fullpath = item.nodeid.split('[')[0].split('/')[1]
            # 获取当前测试项的重复轮次
            pytest_repeat_step_number = item.callspec.indices.get('__pytest_repeat_step_number')
            params = item.callspec.params
            # 如果该item包含data，说明使用了数据，则用data0[-1]获取数据索引
            if 'data' in params:
                data_index = int(item.callspec.id.split('-')[0][-1])
                filename, _, func_name = item_fullpath.split('::')
                # 如果该测试用例的测试数据等于当前session循环次数，则不过滤
                if data_index == pytest_repeat_step_number:
                    filtered_items.append(item)
                # 如果该测试用例的测试数据小于等于session循环次数，则不过滤
                elif data_length[filename][func_name] < session_loop:
                    filtered_items.append(item)
            # 若没有使用数据，则不过滤
            else:
                filtered_items.append(item)

        # 替换原始测试项列表，并保留原有引用
        items[:] = filtered_items

    # 函数独立依赖，保留所有item，无需操作

    # 根据fullpath和loop查找对应item的node_id
    def get_node_id(fullpath: str, loop: int):
        for element in items:
            element_fullpath = element.nodeid.split('[')[0].split('/')[1]
            element_loop = element.callspec.indices.get('__pytest_repeat_step_number')
            if element_loop == loop and element_fullpath == fullpath:
                return element.nodeid

    # 遍历所有测试项，动态添加依赖关系
    for item in items:
        # 获取测试函数的模块名、类名和函数名
        module_name = item.module.__name__ + '.py'
        class_name = item.cls.__name__ if item.cls else None
        func_name = item.originalname
        item_loop = item.callspec.indices.get('__pytest_repeat_step_number')
        dependency_config = Config.dependency_config()

        # 检查是否有配置文件中的依赖关系
        if module_name in dependency_config:
            module_deps = dependency_config[module_name]
            if class_name and class_name in module_deps:
                class_deps = module_deps[class_name]
                if func_name in class_deps:
                    dep_info = class_deps[func_name]
                    scope = dep_info.get('scope', 'session')
                    depends = []
                    if dep_info.get('depends'):
                        for dep in dep_info.get('depends'):
                            if dep in name_to_fullpath:
                                depends.append(get_node_id(name_to_fullpath[dep], item_loop))
                            else:
                                LogUtils().errors(f"未找到依赖项{dep}，请检查依赖项名称是否正确")
                    # 动态添加 dependency marker
                    item.add_marker(
                        pytest.mark.dependency(
                            scope=scope,
                            depends=depends
                        )
                    )


@pytest.fixture(scope="class", autouse=True)
def session_load():
    # 加载session
    Driver().sessionManger.load_session("login")


global cur_item


# 获取测试后的数据
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    global cur_item
    # 只在测试函数调用阶段处理
    if report.when == "setup":
        # 获取测试输入前的item
        cur_item = item
        LogUtils().debug(f"输入数据: {cur_item.funcargs.get('data')}")
    if report.when == "call":
        # 获取测试输入后的item
        cur_item = item
        LogUtils().debug(f"输出数据: {cur_item.funcargs.get('data')}")


# 测试函数日志收集
def pytest_runtest_logreport(report):
    global cur_item
    log_utils = LogUtils()
    node_id = cur_item.nodeid  # 获取测试用例的唯一标识符
    description = cur_item.function.__doc__.strip()  # 获取测试用例描述信息
    data = cur_item.funcargs.get("data", None)
    duration = round(report.duration, 2)  # 获取测试用例执行时间
    assert_result = data.get("assert_result") if data and "assert_result" in data else None
    if report.when == "setup":  # 测试用例开始执行

        log_utils.infos("-------------------test start-------------------")
        log_utils.infos(f"node_id: {node_id}")
        log_utils.infos(f"Description: {description}")
        if data:
            log_utils.infos(f"Data: {data}")
        if report.skipped:  # 测试被跳过
            log_utils.infos(f"Test skipped: {node_id}")
            skipped_reason = f"{report.longrepr[1]},{report.longrepr[2]}"
            log_utils.infos(f"Skipped reason: {skipped_reason}")
    elif report.when == "call":  # 测试用例执行阶段
        if report.passed:  # 测试通过
            log_utils.infos(f"Test passed: {assert_result}")
            log_utils.infos(f"Duration: {duration}s")
        elif report.failed:  # 测试失败
            log_utils.infos(f"Test failed: {assert_result}")
            log_utils.infos(f"Duration: {duration}s")
    elif report.when == "teardown":  # 测试用例结束执行
        log_utils.infos("-------------------test end---------------------")
