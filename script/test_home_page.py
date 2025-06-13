import pytest

from base import Asserts, AssertType
from page_object.operation.home_page import HomePage


class TestHomePage:
    """
    首页模块测试
    """

    def setup_class(self):
        self.home_page = HomePage()

    def setup_method(self, method):
        self.home_page.go_main()

    def test_switch_layer(self, data):
        """
        切换图层
        """
        self.home_page.switch_layer(data['layer'])
        result = self.home_page.get_current_layer()
        Asserts.asserts(data['layer'], result, 'equal')

    def test_view_history_track(self):
        """
        查看历史轨迹
        """
        self.home_page.view_history_track('hy', '出区')
        Asserts.asserts(self.home_page.is_device_video_opened(), True, 'equal')

    def test_real_track(self):
        """
        实时跟踪
        """
        self.home_page.real_track('hy')
        Asserts.asserts(self.home_page.get_track_status(), '正在跟踪', 'in')

    def test_view_device(self):
        """
        查看设备
        """
        self.home_page.view_device('审讯室1')
        Asserts.asserts(self.home_page.is_device_video_opened(), True, 'equal')