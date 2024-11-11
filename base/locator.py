from selenium.common import NoSuchFrameException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

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
    :param driver: WebDriver
    :param element: 元素定位信息
    :return:
    """

    def __init__(self, driver: WebDriver, element: dict = None):
        self.driver = driver
        if element:
            self.method, self.path = next(iter(element.items()))
            # 设定等待时长
            self.driver.implicitly_wait(10)
            wait = WebDriverWait(self.driver, 10)
            # 定位方法验证
            if self.method in ['css', 'xpath']:
                try:
                    # 获取元素
                    web_element = None
                    if self.method == 'css':
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.path)))
                        web_element = self.driver.find_element(By.CSS_SELECTOR, self.path)
                    if self.method == 'xpath':
                        wait.until(EC.presence_of_element_located((By.XPATH, self.path)))
                        web_element = self.driver.find_element(By.XPATH, self.path)
                    wait.until(EC.visibility_of(web_element))
                    self.element = web_element
                    debug_log = f'{self.path}通过{self.method}定位成功！'
                    LogUtils().debug(debug_log)
                except Exception as e:
                    error_log = f'{self.path}通过{self.method}定位失败！{e}'
                    LogUtils().error(error_log)
                    raise Exception(error_log)
            else:
                error_log = f'{self.path}定位方法{self.method}不支持！'
                LogUtils().error(error_log)
                raise Exception(error_log)

    # 点击操作
    def click(self):
        try:
            self.element.click()
            debug_log = f'{self.path}点击！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.path}点击失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)

    # 输入操作
    def send_keys(self, text):
        try:
            if text:
                # clear()函数不起作用，使用全选输入
                self.element.send_keys(Keys.CONTROL, 'a')
                self.element.send_keys(text)
                debug_log = f'{self.path}输入{text}！'
                LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'{self.path}输入{text}失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)

    # 获取文本
    def get_text(self):
        try:
            text = self.element.text
            debug_log = f'{self.path}获取文本{text}！'
            LogUtils().debug(debug_log)
            return text
        except Exception as e:
            error_log = f'{self.path}获取文本失败！{e}'
            LogUtils().error(error_log)
            raise

    # 跳转网页
    def goto(self, url):
        try:
            self.driver.get(url)
            debug_log = f'跳转到{url}！'
            LogUtils().debug(debug_log)
        except Exception as e:
            error_log = f'跳转到{url}失败！{e}'
            LogUtils().error(error_log)
            raise Exception(error_log)
