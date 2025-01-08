from enum import Enum, auto
from typing import Union

from common import LogUtils


class AssertType(Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    IN = auto()
    NOT_IN = auto()

    @staticmethod
    def from_string(assert_type_str) -> Enum:
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
    assert_result: bool = False

    @staticmethod
    def __assert_equal(result, expect):
        """
        相等断言
        :param result:结果
        :param expect: 预期
        :return: 无
        """
        try:
            assert result == expect, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            Asserts.assert_result = True
            info_log = f'相等断言成功,预期：{expect},实际：{result}'
            LogUtils().infos(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            log = f'相等断言失败,预期：{expect},实际：{result}'
            LogUtils().logs(log)
            raise e

    @staticmethod
    def __assert_not_equal(result, expect):
        """
        相等断言
        :param result:结果
        :param expect: 预期
        :return: 无
        """
        try:
            assert result != expect, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            Asserts.assert_result = True
            info_log = f'不等断言成功,预期：{expect},实际：{result}'
            LogUtils().infos(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            log = f'不等断言失败,预期：{expect},实际：{result}'
            LogUtils().logs(log)
            raise e

    @staticmethod
    def __assert_in(result, expect):
        """
        包含断言
        :param result:结果
        :param expect: 预期
        :return: 无
        """
        try:
            assert expect in result, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            Asserts.assert_result = True
            info_log = f'包含断言成功,预期：{expect},实际：{result}'
            LogUtils().infos(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            log = f'包含断言失败,预期：{expect},实际：{result}'
            LogUtils().logs(log)
            raise e

    @staticmethod
    def __assert_not_in(result, expect):
        """
        包含断言
        :param result:结果
        :param expect: 预期
        :return: 无
        """
        try:
            assert expect not in result, '预期结果：{0} 实际结果：{1}'.format(expect, result)
            Asserts.assert_result = True
            info_log = f'不包含断言成功,预期：{expect},实际：{result}'
            LogUtils().infos(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            log = f'不包含断言失败,预期：{expect},实际：{result}'
            LogUtils().logs(log)
            raise e

    @staticmethod
    def asserts(assert_type: Union[AssertType, str], result, expect):
        """
        断言
        :param assert_type: 断言类型（使用 AssertType 枚举）
        :param result: 结果
        :param expect: 预期
        :return: 无
        """
        if isinstance(assert_type, str):
            assert_type = AssertType.from_string(assert_type)

        assert_mapping = {
            AssertType.EQUAL: Asserts.__assert_equal,
            AssertType.NOT_EQUAL: Asserts.__assert_not_equal,
            AssertType.IN: Asserts.__assert_in,
            AssertType.NOT_IN: Asserts.__assert_not_in,
        }
        assert assert_type in assert_mapping, f"Unsupported assert type: {assert_type}"
        assert_mapping[assert_type](result, expect)
