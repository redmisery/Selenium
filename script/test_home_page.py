import pytest

from base import Asserts, AssertType
from page_object.operation.home_page import HomePage


class TestHomePage:
    def setup_class(self):
        self.home_page = HomePage()

    @pytest.mark.dependency(depends=["script/test_login.py::TestLogin::test_login[data1]"], scope='session')
    def test_switch_layer(self):
        self.home_page.go_main()
        self.home_page.switch_layer('4楼')
        result = self.home_page.get_current_layer()
        Asserts.asserts(AssertType.EQUAL, result, '4楼')
