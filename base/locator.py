from typing import Union

from selenium.common import NoSuchFrameException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from base.driver import Driver
from base.element import Element
from common import LogUtils, PublicData


# 上下文Frame切换器
class SwitchFrame:
    """
    上下文Frame切换器
    """

    def __init__(self, driver: WebDriver, frame_ref):
        self.driver = driver
        self.frame_ref = frame_ref

    def __enter__(self):
        try:
            self.driver.switch_to.frame(self.frame_ref)
        except NoSuchFrameException as e:
            error_log = f'{self.frame_ref} frame not found!{e} '
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.driver.switch_to.default_content()
        except Exception as e:
            error_log = f'return main frame failed!{e} '
            LogUtils().errors(error_log)
            raise Exception(error_log)


# 元素定位器
class Locator:
    """
    元素定位器
    自带driver，无需显式调用driver
    :param element: 元素
    :return:
    """

    def __init__(self, element: Element = None, appendix_element: Element = None):
        """
        初始化
        :param element: 元素
        """
        self.driver = Driver().driver
        self.element = Union[Element, None]
        self.web_element = Union[WebElement, None]
        self.web_elements = Union[list[WebElement], None]
        self.path = Union[str, None]
        self.element = element
        # 隐式等待
        self.driver.implicitly_wait(10)
        # 显式等待
        self.wait = WebDriverWait(self.driver, 10)
        if element:
            # 若存在appendix_element，则合并path
            if appendix_element and element.method == appendix_element.method:
                element.path = element.path + appendix_element.path
            self.load_element(element)

    def load_element(self, element: Element):
        """
        加载元素
        """
        self.element = element
        self.path = self.element.path
        try:
            self.web_element = self.wait.until(EC.presence_of_element_located((element.method, self.path)))
            debug_log = f'{self.path}元素定位成功！'
            LogUtils().debug(debug_log)
            return self
        except Exception as e:
            error_log = f'{self.path}元素定位失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def load_elements(self, element: Element):
        """
        加载元素列表
        """
        self.element = element
        self.path = self.element.path
        try:
            self.web_elements = self.wait.until(EC.presence_of_all_elements_located((element.method, self.path)))
            debug_log = f'{self.path}元素定位成功！'
            LogUtils().debug(debug_log)
            return self
        except Exception as e:
            error_log = f'{self.path}元素定位失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def switch_frame(self, element: Element):
        """
        切换Frame
        """
        try:
            self.driver.switch_to.frame(self.load_element(element).web_element)
            debug_log = f'切换Frame{self.path}成功！'
            LogUtils().debug(debug_log)
        except NoSuchFrameException as e:
            error_log = f'{self.path} frame not found!{e} '
            LogUtils().errors(error_log)
            raise Exception(error_log)
        except Exception as e:
            error_log = f'切换Frame{self.path}失败！{e} '
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def click(self):
        """
        单击操作
        """
        try:
            self.web_element.click()
            debug_log = f'{self.path}元素点击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.path}点击失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def double_click(self):
        """
        双击操作
        """
        try:
            actions = ActionChains(self.driver)
            actions.double_click(self.web_element).perform()
            debug_log = f'{self.path}元素双击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.path}双击失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def input(self, text):
        """
        输入操作
        """
        try:
            if text:
                # clear()函数不起作用，使用全选输入
                self.web_element.send_keys(Keys.CONTROL, 'a')
                self.web_element.send_keys(text)
                debug_log = f'{self.path}输入{text}！'
                LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.path}输入{text}失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    def get_text(self):
        """
        获取文本
        """
        try:
            # 通过js获取文本，可以解决部分元素获取文本为空的问题，原因是元素被隐藏或不可见
            text = self.driver.execute_script("return arguments[0].innerText", self.web_element)
            debug_log = f'{self.path}获取文本{text}！'
            LogUtils().debug(debug_log)
            return text
        except Exception as e:
            error_log = f'{self.path}获取文本失败！{e}'
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
            actions.move_to_element(self.web_element).perform()
            actions.pause(hover_time).perform()
            debug_log = f'{self.path}元素悬停{hover_time}秒！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.path}悬停失败！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    # 等待页面完全加载
    def wait_for_page_load(self):
        """
        等待页面完全加载
        """
        try:
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            debug_log = f'页面{self.driver.current_url}加载完成！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'页面{self.driver.current_url}加载超时！{e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)
