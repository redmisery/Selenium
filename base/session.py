import pickle

from common import LogUtils, Config


class SessionManager:
    session_path = Config().project_path / 'data' / 'session'

    def __init__(self, driver):
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.driver = driver

    def save_session(self, session_name):
        """
        保存当前会话的Cookies
        """
        try:
            cookies = self.driver.get_cookies()
            with open(self.session_path / f'{session_name}_cookies.pkl', 'wb') as file:
                pickle.dump(cookies, file)
            LogUtils().debug(f'Session saved as {session_name}_cookies.pkl')
        except Exception as e:
            LogUtils().error(f'Failed to save session: {e}')

    def load_session(self, session_name):
        """
        从保存的Cookies中恢复会话
        """
        try:
            with open(self.session_path / f'{session_name}_cookies.pkl', 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            LogUtils().debug(f'Session loaded from {session_name}_cookies.pkl')
        except Exception as e:
            LogUtils().error(f'Failed to load session: {e}')

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
            LogUtils().error(f'Failed to delete session cookies: {e}')
