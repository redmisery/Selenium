import pytest

from page_object import Foundation


class TestFoundation:
    """
    基础模块测试
    """
    foundation = Foundation()

    @pytest.mark.dependency(scope="session")
    def test01(self):
        pass
