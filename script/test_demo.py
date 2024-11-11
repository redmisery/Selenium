from common.data_loader import Excel

excel_file = 'test_login'


def pytest_generate_tests(metafunc):
    # 获取当前测试函数的名称
    function_name = metafunc.function.__name__

    # 根据函数名称过滤数据
    data = Excel(function_name).read()

    # 参数化测试
    metafunc.parametrize("test_data", data)


def test_my_function(test_data):
    # 使用test_data做测试
    # assert test_data['input'] == test_data['expected']  # 示例断言
    print(test_data)