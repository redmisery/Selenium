from selenium.common import NoSuchFrameException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from base import Driver
from base.element import Element
from common import LogUtils


# 上下文Frame切换器
class SwitchFrame:
    def __init__(self, driver: WebDriver, frame_ref):
        self.driver = driver
        self.frame_ref = frame_ref

    def __enter__(self):
        try:
            self.driver.switch_to.frame(self.frame_ref)
        except NoSuchFrameException as e:
            error_log = f'{self.frame_ref} frame not found!{e} '
            LogUtils().error(error_log)
            raise Exception(error_log)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.driver.switch_to.default_content()
        except Exception as e:
            error_log = f'return main frame faild!{e} '
            LogUtils().error(error_log)
            raise Exception(error_log)


# 元素定位器
class Locator:
    """
    元素定位器
    :param element: 元素
    :return:
    """

    def __init__(self, element: Element = None):
        self.driver = Driver().driver
        self.element = element
        self.web_element = None
        # 隐式等待
        self.driver.implicitly_wait(10)
        # 显式等待
        wait = WebDriverWait(self.driver, 10)
        if element:
            try:
                self.web_element = wait.until(EC.presence_of_element_located((element.method, element.path)))
            except Exception as e:
                error_log = f'{element.path}元素定位失败！{e}'
                LogUtils().error(error_log)
                raise Exception(error_log)

    def click(self):
        """
        单击操作
        """
        try:
            self.web_element.click()
            debug_log = f'{self.element.path}元素点击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.element.path}点击失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)

    def double_click(self):
        """
        双击操作
        """
        try:
            actions = ActionChains(self.driver)
            actions.double_click(self.web_element).perform()
            debug_log = f'{self.element.path}元素双击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.element.path}双击失败！{e}'
            LogUtils().error(error_log)
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
                debug_log = f'{self.element.path}输入{text}！'
                LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.element.path}输入{text}失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)

    def get_text(self):
        """
        获取文本
        """
        try:
            # 通过js获取文本，可以解决部分元素获取文本为空的问题，原因是元素被隐藏或不可见
            text = self.driver.execute_script("return arguments[0].innerText", self.web_element)
            debug_log = f'{self.element.path}获取文本{text}！'
            LogUtils().debug(debug_log)
            return text
        except Exception as e:
            error_log = f'{self.element.path}获取文本失败！{e}'
            LogUtils().error(error_log)
            raise

    def goto(self, url):
        """
        跳转url
        """
        try:
            self.driver.get(url)
            debug_log = f'跳转到{url}！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'跳转到{url}失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)

    def hover(self):
        """
        鼠标悬停操作
        """
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(self.web_element).perform()
            debug_log = f'{self.element.path}元素悬停！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.element.path}悬停失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)