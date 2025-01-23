from enum import Enum, auto
from typing import Union

from common import LogUtils


class AssertType(Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    IN = auto()
    NOT_IN = auto()

    @staticmethod
    def from_string(assert_type_str) -> 'AssertType':
        """
        从字符串获取断言类型枚举
        :param assert_type_str: 断言类型字符串
        :return: AssertType 枚举成员
        """
        assert_type_mapping = {
            'equal': AssertType.EQUAL,
            'not_equal': AssertType.NOT_EQUAL,
            'in': AssertType.IN,
            'not_in': AssertType.NOT_IN,
        }
        return assert_type_mapping.get(assert_type_str.lower())


class Asserts:
    """
    断言类
    """

    @staticmethod
    def __assert_equal(result, expect):
        """
        相等断言
        :param result: 结果
        :param expect: 预期结果
        :return: (断言结果, 日志信息)
        """
        try:
            assert result == expect, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            return True, f'assert_result:相等断言成功,预期：{expect},实际：{result}'
        except AssertionError as e:
            return False, f'assert_result:相等断言失败,预期：{expect},实际：{result}'

    @staticmethod
    def __assert_not_equal(result, expect):
        """
        不等断言
        :param result: 结果
        :param expect: 预期结果
        :return: (断言结果, 日志信息)
        """
        try:
            assert result != expect, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            return True, f'assert_result:不等断言成功,预期：{expect},实际：{result}'
        except AssertionError as e:
            return False, f'assert_result:不等断言失败,预期：{expect},实际：{result}'

    @staticmethod
    def __assert_in(result, expect):
        """
        包含断言
        :param result: 结果
        :param expect: 预期结果
        :return: (断言结果, 日志信息)
        """
        try:
            assert expect in result, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            return True, f'assert_result:包含断言成功,预期：{expect},实际：{result}'
        except AssertionError as e:
            return False, f'assert_result:包含断言失败,预期：{expect},实际：{result}'

    @staticmethod
    def __assert_not_in(result, expect):
        """
        不包含断言
        :param result: 结果
        :param expect: 预期结果
        :return: (断言结果, 日志信息)
        """
        try:
            assert expect not in result, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            return True, f'assert_result:不包含断言成功,预期：{expect},实际：{result}'
        except AssertionError as e:
            return False, f'assert_result:不包含断言失败,预期：{expect},实际：{result}'

    @staticmethod
    def asserts(data: Union[dict, str], result, assert_type=None):
        """
        断言，支持两种使用方式
        方式1: 传入断言数据字典，包含预期结果和断言类型
        方式2: 传入预期结果和断言类型，预期结果为字符串
        :param data: 断言数据字典或预期结果
        :param data: 测试数据
        :param result: 运行结果
        :param assert_type: 断言类型
        :return: 断言结果
        """
        assert_mapping = {
            AssertType.EQUAL: Asserts.__assert_equal,
            AssertType.NOT_EQUAL: Asserts.__assert_not_equal,
            AssertType.IN: Asserts.__assert_in,
            AssertType.NOT_IN: Asserts.__assert_not_in,
        }
        # 检测必要字段
        if isinstance(data, dict):
            expect = data['expect']
            necessary_keys = ['assert_type', 'expect']
            for key in necessary_keys:
                if key not in data:
                    error_log = f'assert_result:断言数据不完整,缺少{key}字段,数据：{data}'
                    LogUtils().errors(error_log)
                    raise ValueError(f'断言数据不完整,缺少{key}字段')

            # 判断断言类型是否存在并获取断言类型
            assert_type = data['assert_type']

        else:
            expect = data
        assert_type = AssertType.from_string(assert_type)
        assert assert_type in assert_mapping, f"Unsupported assert type: {assert_type}"

        # 执行断言
        success, log = assert_mapping[assert_type](result, expect)
        if isinstance(data,dict):
            data.update({'assert_result': log})
        else:
            LogUtils().infos(log)

        if not success:
            raise AssertionError(log)
