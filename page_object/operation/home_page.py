from typing import Literal
from base import Page, Locator
from common import LogUtils, singleton


@singleton
class HomePage:
    """
    首页
    """

    def __init__(self):
        self.page = Page().load()
        self.locator = Locator()
        # 进入时默认切换到对应模块
        # Foundation().switch_module('首页')

    def go_main(self):
        self.locator.goto('/index.html#/svmsweb_jg/bdms/map')
        # 开始切换内部iframe，并统一使用定位器
        self.locator.switch_frame(self.page.frame)

    # 切换图层
    def switch_layer(self, layer_name):
        self.locator.load_element(self.page.map_layer.first_layer)
        if self.locator.get_text() != layer_name:
            self.locator.hover()
            web_elements = self.locator.load_elements(self.page.map_layer.other_layers).web_elements
            flag = False
            for index, web_element in enumerate(web_elements):
                self.locator.path = self.page.map_layer.other_layers.path + f'[{index}]'
                self.locator.web_element = web_element
                if self.locator.get_text() == layer_name:
                    self.locator.click()
                    flag = True
                    break
            if not flag:
                error_log = f"切换图层失败，图层名称：{layer_name} 不存在"
                LogUtils().errors(error_log)
        else:
            debug_info = f"当前图层已是：{layer_name}"
            LogUtils().debug(debug_info)

    # 获取当前图层名称
    def get_current_layer(self):
        layer_name = self.locator.load_element(self.page.map_layer.first_layer).get_text()
        return layer_name

    # 查看历史轨迹
    def view_history_track(self, person_name, person_location: Literal['在区', '出区'], person_type: Literal['民警', '嫌疑人', '其他'] = None):
        self.locator.load_element(self.page.track_mode.history).click()
        self.locator.load_element(self.page.track_mode.history.search_input).send_keys(person_name)
        if person_location == '在区':
            self.locator.load_element(self.page.track_mode.history.person_location.in_area).click()
        if person_location == '出区':
            self.locator.load_element(self.page.track_mode.history.person_location.out_area).click()
        if person_type:
            type_dict = {'民警': 'police', '嫌疑人': 'suspect', '其他': 'others'}
            self.locator.load_element(self.page.track_person.history.person_type + type_dict[person_type]).click()
        self.locator.load_element(self.page.track_person.history.search).click()
        self.locator.load_elements()

    # 实时跟踪
    def real_track(self, person_name, person_type: Literal['民警', '嫌疑人', '其他'] = None):
        self.locator.load_element(self.page.track_mode.real_time).click()
