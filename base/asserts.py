from common import LogUtils


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
            LogUtils().info(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            info_log = f'相等断言失败,预期：{expect},实际：{result}'
            LogUtils().info(info_log)
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
            LogUtils().info(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            info_log = f'不等断言失败,预期：{expect},实际：{result}'
            LogUtils().info(info_log)
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
            LogUtils().info(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            info_log = f'包含断言失败,预期：{expect},实际：{result}'
            LogUtils().info(info_log)
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
            LogUtils().info(info_log)
        except AssertionError as e:
            Asserts.assert_result = False
            info_log = f'不包含断言失败,预期：{expect},实际：{result}'
            LogUtils().info(info_log)
            raise e

    @staticmethod
    def asserts(assert_type, result, expect):
        """
        断言
        :param assert_type:断言类型
        :param result:结果
        :param expect: 预期
        :return: 无
        """
        if assert_type == 'equal':
            Asserts.__assert_equal(result,expect)
        elif assert_type == 'not_equal':
            Asserts.__assert_not_equal(result, expect)
        elif assert_type == 'in':
            Asserts.__assert_in(result,expect)
        elif assert_type == 'not in':
            Asserts.__assert_not_in(result,expect)