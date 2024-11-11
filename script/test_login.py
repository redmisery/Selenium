from base import Driver
from base.asserts import Asserts
from common import PublicData
from page_object.index import Index


class TestLogin:
    index = Index()
    constant_data = PublicData.get_constant_data()

    def test_login(self, data):
        ip = self.constant_data['spgz_ip']
        url = f'http://{ip}/'
        self.index.launch_index(url)
        self.index.username_input(data['username'])
        self.index.password_input(data['password'])
        self.index.click_confirm()
        # 根据expect有不同的断言方式
        try:
            if 'http' in data['expect']:
                result = self.index.driver.current_url
            else:
                result = self.index.get_login_tip()
            Asserts.asserts(data['assert_type'], result, data['expect'])
        except AssertionError as e:
            raise e
        finally:
            if Asserts.assert_result:
                Driver().sessionManger.save_session('login')
            Driver().sessionManger.delete_session()
