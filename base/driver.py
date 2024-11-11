import traceback

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service

from base.chrome_driver_update import ChromeDriverUpdate
from base.session import SessionManager
from common import LogUtils


class Driver:
    """
    驱动类
    """
    instance = None

    def __new__(cls):
        path = ChromeDriverUpdate(Update_interval_time=24).install()
        service = Service(executable_path=path)
        if cls.instance is None:
            cls.instance = super(Driver, cls).__new__(cls)
            cls.instance.driver = Chrome(service=service)
            # 驱动启动起始位置
            cls.instance.driver.set_window_position(-8, 0, windowHandle='current')
            # 驱动启动起始大小
            cls.instance.driver.set_window_size(1920, 1080, windowHandle='current')
            cls.instance.sessionManger = SessionManager(cls.instance.driver)
        debug_log = f'{path}  Driver first created!'
        LogUtils().debug(debug_log)
        return cls.instance

    # 关闭driver
    @staticmethod
    def close_driver():
        try:
            Driver.driver.quit()
            debug_log = 'Driver closed'
            LogUtils().debug(debug_log)
            Driver.driver = None  # 重置驱动实例
            Driver.sessionManger = None  # 重置session管理实例
        except Exception as e:
            error_log = f'Driver close failed!{e} {traceback.format_exc()}'
            LogUtils().error(error_log)
            raise Exception(error_log)