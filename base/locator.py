from typing import Union, Optional, List
from selenium.common import NoSuchFrameException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from base.driver import Driver
from base.element import Element
from common import LogUtils, PublicData


class Locator:
    """元素定位器，支持链式元素加载和基础操作"""
    wait_time = 10

    def __init__(self, element: Optional[Element] = None, parent: Optional['Locator'] = None, web_element: Optional[WebElement] = None):
        """
        初始化定位器
        """
        self.driver = Driver().driver
        # 父节点
        self._parent = parent
        self._element = element
        self._web_element = web_element

        if element and not web_element:
            self._locate_element()

    def _locate_element(self):
        """执行元素定位核心逻辑"""
        try:
            # 当存在parent_element时，说明存在父节点，需要根据父节点进行定位
            if self._parent:
                # 父节点未定位，先定位父节点
                if not self._parent._web_element:
                    self._parent._locate_element()
                self._web_element = WebDriverWait(self._parent._web_element, self.wait_time).until(
                    EC.presence_of_element_located(
                        (self._element.method, self._element.path)
                    )
                )
                LogUtils().debug(f"子元素定位成功 | 父: {self._parent._element.path} ➔ 子: {self._element.path}")
            # 否则直接使用element进行定位
            else:
                self._web_element = WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((self._element.method, self._element.path))
                )
                LogUtils().debug(f"元素定位成功: {self._element.path}")
        except Exception as e:
            error_msg = f"元素定位失败: {self._element.path} - {str(e)}"
            LogUtils().error(error_msg)
            raise Exception(error_msg)

    def load_element(self, element: Element) -> 'Locator':
        """加载子元素（返回新Locator实例实现链式）"""
        if self._parent:
            return Locator(element=element, parent=self)
        else:
            return Locator(element=element)

    def load_elements(self, element: Element) -> List['Locator']:
        """加载元素列表（支持链式操作）"""
        try:
            # 定位所有元素
            context = self._parent._web_element if self._parent else self.driver
            web_elements = WebDriverWait(context, self.wait_time).until(
                EC.presence_of_all_elements_located(
                    (self._element.method, self._element.path)
                )
            )
            parent = self._parent if self._parent else None
            return [
                Locator(Element(method=element.method, path=f"{element.path}[{i + 1}]"), parent=parent, web_element=el)
                for i, el in enumerate(web_elements)
            ]
        except Exception as e:
            error_msg = f"元素列表定位失败: {element.path} - {str(e)}"
            LogUtils().error(error_msg)
            raise Exception(error_msg)

    def switch_frame(self):
        """
        切换Frame
        """
        try:
            self.driver.switch_to.frame(self._web_element)
            debug_log = f'切换Frame{self._element.path}成功！'
            LogUtils().debug(debug_log)
        except NoSuchFrameException as e:
            error_log = f'{self._element.path} frame not found!{e} '
            LogUtils().errors(error_log)
            raise Exception(error_log)
        except Exception as e:
            error_log = f'切换Frame{self._element.path}失败！{e} '
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def click(self):
        """
        单击操作
        """
        try:
            self._web_element.click()
            debug_log = f'{self._element.path}元素点击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self._element.path}点击失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def double_click(self):
        """
        双击操作
        """
        try:
            actions = ActionChains(self.driver)
            actions.double_click(self._web_element).perform()
            debug_log = f'{self._element.path}元素双击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self._element.path}双击失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def input(self, text):
        """
        输入操作
        """
        try:
            if text:
                # clear()函数不起作用，使用全选输入
                self._web_element.send_keys(Keys.CONTROL, 'a')
                self._web_element.send_keys(text)
                debug_log = f'{self._element.path}输入{text}！'
                LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self._element.path}输入{text}失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def get_text(self):
        """
        获取文本
        """
        try:
            # 通过js获取文本，可以解决部分元素获取文本为空的问题，原因是元素被隐藏或不可见
            text = self.driver.execute_script("return arguments[0].innerText", self._web_element)
            debug_log = f'{self._element.path}获取文本{text}！'
            LogUtils().debug(debug_log)
            return text
        except Exception as e:
            error_log = f'{self._element.path}获取文本失败！{e}'
            LogUtils().errors(error_log)
            raise

    def goto(self, api=None):
        """
        跳转到指定api
        :param api: api,若为空则直接访问ip
        """
        ip = PublicData.get_constant_data()['spgz_ip']
        protocol = 'http://'
        try:
            # api格式验证
            if api and not api.startswith('/'):
                api = f'/{api}'
            if not api:
                url = f'{protocol}{ip}'
            else:
                url = f'{protocol}{ip}{api}'
            self.driver.get(url)
            self.wait_for_page_load()
            debug_log = f'跳转到{url}！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'跳转到{api}失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def hover(self, hover_time: Union[int, None] = 1):
        """
        鼠标悬停操作，默认3秒
        """
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(self._web_element).perform()
            actions.pause(hover_time).perform()
            debug_log = f'{self._element.path}元素悬停{hover_time}秒！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self._element.path}悬停失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    # 等待页面完全加载
    def wait_for_page_load(self):
        """
        等待页面完全加载
        """
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            debug_log = f'页面{self.driver.current_url}加载完成！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'页面{self.driver.current_url}加载超时！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)
