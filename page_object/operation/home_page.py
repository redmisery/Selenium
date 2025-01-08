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