import pytest

from base import Asserts, AssertType
from page_object.operation.home_page import HomePage


class TestHomePage:
    def setup_class(self):
        self.home_page = HomePage()

    def test_switch_layer(self,data):
        """
        切换图层
        """
        self.home_page.go_main()
        self.home_page.switch_layer(data['layer'])
        result = self.home_page.get_current_layer()
        Asserts.asserts(data['layer'], result, 'equal')
