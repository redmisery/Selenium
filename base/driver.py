import os
import pickle
import traceback
from pathlib import Path

from base.webdriver import WebDriver as Chrome, WebDriver
from common import singleton, LogUtils


@singleton
class Driver:
    """
    驱动类
    description: 由于Selenium的驱动启动过程比较耗时，因此这里使用单例模式，避免每次都要启动驱动,
                 同时Selenium升级到4.26.1后，会自动获取最新驱动，无需手动更新，在此不使用本地chrome_driver_update包
                 首次启动时间较长，请耐心等待。
                 驱动环境配置文件：env/se-config.env
    """

    def __init__(self):
        try:
            self.driver = Chrome()
            driver_path = self.driver.service.path
            # 驱动启动起始位置
            self.driver.set_window_position(-8, 0, windowHandle='current')
            # 驱动启动起始大小
            self.driver.set_window_size(1920, 1080, windowHandle='current')
            # 实例化session管理器
            self.sessionManger = SessionManager(self.driver)
            debug_log = f'驱动路径：{driver_path}！  Driver first created!'
            LogUtils().debug(debug_log)
        except RuntimeError as e:
            error_log = f'驱动启动失败！{e} {traceback.format_exc()}'
            LogUtils().logs("error", "debug", msg=error_log)
            raise RuntimeError(error_log)

    # 关闭driver
    @staticmethod
    def close_driver(self):
        try:
            self.driver.quit()
            debug_log = 'Driver closed'
            LogUtils().debug(debug_log)
            self.sessionManger = None  # 重置session管理实例
        except Exception as e:
            error_log = f'Driver close failed!{e} {traceback.format_exc()}'
            LogUtils().logs("error", "debug", msg=error_log)
            raise Exception(error_log)


class SessionManager:

    def __init__(self, driver: WebDriver):
        self.session_path = Path(os.getenv('HOME')) / 'data' / 'session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.driver = driver

    def save_session(self, session_name):
        """
        保存当前会话的Cookies
        """
        try:
            cookies = self.driver.get_cookies()
            cookies_path = self.session_path / f'{session_name}_cookies.pkl'
            cookies_path.write_bytes(pickle.dumps(cookies))
            LogUtils().debug(f'Session saved as {session_name}_cookies.pkl')
        except Exception as e:
            LogUtils().errors(f'Failed to save session: {e}')

    def load_session(self, session_name):
        """
        从保存的Cookies中恢复会话
        """
        cookies_path = self.session_path / f'{session_name}_cookies.pkl'
        try:
            with open(cookies_path, 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    try:
                        domain = cookie.get('domain')
                        if domain not in self.driver.current_url:
                            protocol = 'https' if 'https' in self.driver.current_url else 'http'
                            # 加载cookie之前先访问对应域名，否则可能导致cookie失效
                            self.driver.get(f'{protocol}://{domain}')
                        self.driver.add_cookie(cookie)
                        LogUtils().debug(f'Cookie added:{cookie}')
                    except Exception as e:
                        LogUtils().errors(f'Failed to add cookie:{cookie} {e}')
            LogUtils().debug(f'Session loaded from {session_name}_cookies.pkl')
        except Exception as e:
            LogUtils().errors(f'Failed to load session_file:{cookies_path} {e}')

    def delete_session(self):
        """
        清除当前会话的Cookies、缓存
        """
        try:
            self.driver.delete_all_cookies()
            # 清理cookie后，还需要清理浏览器本地数据
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            LogUtils().debug('Session cookies deleted')
        except Exception as e:
            LogUtils().errors(f'Failed to delete session cookies: {e}')
