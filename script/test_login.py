from base import Asserts
from base import Driver
from page_object import Index


class TestLogin:
    index = Index()
    driver = Driver().driver

    def test_login(self, data):
        """
        登录测试
        """
        Driver().sessionManger.delete_session()
        self.index.launch_index()
        self.index.username_input(data['username'])
        self.index.password_input(data['password'])
        self.index.click_confirm()
        self.index.locator.wait_for_page_load()
        # 根据expect有不同的断言方式
        try:
            if 'http' in data['expect']:
                result = self.driver.current_url
            else:
                result = self.index.get_login_tip()
            Asserts.asserts(data, result)
            # 登录成功后保存session
            if data['is_success_login']:
                Driver().sessionManger.save_session('login')
        except AssertionError as e:
            raise e
