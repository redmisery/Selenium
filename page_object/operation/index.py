from base import Locator
from base import Page
from common import singleton


@singleton
class Index:
    def __init__(self):
        self.page = Page().load()
        self.locator = Locator()

    # 启动首页
    def launch_index(self):
        self.locator.goto()

    # 用户名输入
    def username_input(self, username):
        self.locator.load_element(self.page.user_text).input(username)

    # 密码输入
    def password_input(self, password):
        self.locator.load_element(self.page.password_text).input(password)

    # 登录确认
    def click_confirm(self):
        self.locator.load_element(self.page.confirm_button).click()

    # 获取登录提示文本
    def get_login_tip(self):
        return self.locator.load_element(self.page.login_tip).get_text()
