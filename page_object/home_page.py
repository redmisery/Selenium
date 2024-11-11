from base.driver import Driver
from common import PublicData


class HomePage:
    driver = Driver.driver
    public_data = PublicData()
    # 平台名称
    software_name = '#root > div > div.container___2L9JH.theme0___11dSN > div.titlebar___GyWMy > div.title___2Meyb > span'
    # 修改名称弹窗
    software_name_pop = 'xpath=/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[1]/span[2]'
    software_name_input = 'xpath=/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/input'
    # software_name_change_confirm = f'//*[@class="ant-btn ant-btn-primary"]'
    software_name_change_confirm = 'xpath=/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/button[2]/span'
    software_name_change_cancel = 'xpath=/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/button[1]/span'

    # 版本信息
    version_information = 'xpath=///*[@id="root"]/div/div[3]/div[3]/label[2]/span[2]'
    # 设置
    setting = 'xpath=//*[@id="root"]/div/div[1]/div[1]/div[2]/div[2]/span/svg'
    # 用户
    user = 'xpath=//*[@id="root"]/div/div[1]/div[1]/div[2]/div[3]/h5'
    # 用户--修改密码
    modify_password = 'xpath=//html/body/div[3]/div/div/ul/li[1]/span/span[2]'
    # 用户--注销登录
    logout = 'xpath=/html/body/div[3]/div/div/ul/li[3]/span/span[2]'
    
    # 数据
    # input
    change_software_name = '视频轨迹跟踪平台软件'
    origin_software_name = '视频轨迹跟踪平台软件'

    def modify_software_name(self, new_name=change_software_name):
        """
        修改平台名称
        public_data:software_name
        :param new_name:新平台名称
        """
        page = self.page
        page.locator(self.software_name).dblclick()
        page.locator(self.software_name_input).fill(new_name)
        page.locator(self.software_name_change_confirm).click()
        result = page.locator(self.software_name).text_content()
        self.public_data.put('software_name', result)

    def restore_software_name(self):
        """
        还原平台名称
        :return:
        """
        page = self.page
        page.locator(self.software_name).dblclick()
        page.locator(self.software_name_input).fill(self.origin_software_name)
        page.locator(self.software_name_change_confirm).click()
        page.locator(self.software_name).text_content()


# 内置3D地图
class InnerMap:
    # iframe的xpath
    iframe_xpath = '//*[@id="common_frame"]/div/iframe'

    browser_instance = Browser.get_instance()
    browser = browser_instance.browser
    # 上一层页面page对象
    page = browser_instance.page
    inner_map = page.frame_locator(iframe_xpath)
    public_data = PublicData()
    # 第一个图层
    map_layer_first = 'xpath=//*[@id="root"]/div/div[3]/div[1]/span'
    # 其他图层所有子元素(数组)
    map_layer_others = 'xpath=//*[@id="root"]/div/div[3]/div[1]/div/div/div/ul'
    # 地图正在加载提示
    lodding_map_layer = 'xpath=//div/div/div/h2'
    # 3D/2D 图形切换
    three_dimensions = 'xpath=//*[@id="root"]/div/div[3]/div[2]/label[1]'
    two_dimensions = 'xpath=//*[@id="root"]/div/div[3]/div[2]/label[2]/span[2]'
    # 实时轨迹
    real_track = 'xpath=//*[@id="root"]/div/div[3]/div[3]/label[1]/span[2]'
    # 历史轨迹
    history_track = 'xpath=//*[@id="root"]/div/div[3]/div[3]/label[2]/span[2]'
    # 人员分布
    personnel_distribution = 'xpath=//*[@id="root"]/div/div[2]/div[1]/text()'
    # 人员分布--民警
    policeman = 'xpath=//*[@id="root"]/div/div[2]/div[3]/div/div/div/div[2]/div/div[2]/div/div[1]/label[1]/span[1]/input'
    # 人员分布--嫌疑人
    criminal_suspect = 'xpath=//*[@id="root"]/div/div[2]/div[3]/div/div/div/div[2]/div/div[2]/div/div[1]/label[2]/span[1]/input'
    # 人员分布--其他人员
    others = 'xpath=//*[@id="root"]/div/div[2]/div[3]/div/div/div/div[2]/div/div[2]/div/div[1]/label[3]/span[1]/input'
    # 设备列表
    devices = 'xpath=//*[@id="root"]/div/div[2]/div[2]/text()'
    # 设备列表--监控
    ipc_list = 'xpath=//*[@id="root"]/div/div[2]/div[4]/div/div/div/div[2]/div/div[2]/div/div/div/div'
    # 所有设备(数组)
    ipcs = 'xpath=//*[@id="root"]/div/div[2]/div[4]/div/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div/ul'

    # 图层切换
    def change_map_layer(self):
        """
        切换所有图层，若都切换成功，返回True，否则返回False
        成功：等待10s，若没有提示，则切换成功
        :return: True/Flase
        """
        page = self.page
        inner_map = self.inner_map

        inner_map.hover(self.map_layer_first)
        inner_map.wait_for_timeout(1000)
        other_layers_name = page.locator(self.map_layer_others).text_content()
        flag_text = '正在下载地图'
        try:
            for layer in other_layers_name:
                inner_map.get_by_text(layer).click()
                # 等待flag_text出现
                inner_map.wait_for_selector(self.lodding_map_layer, state='attached', has_text=flag_text, timeout=10000)
                # 等待flag_text消失
                inner_map.wait_for_selector(self.lodding_map_layer, state='hidden', has_text=flag_text, timeout=10000)
            return True
        except TimeoutError:
            return False
