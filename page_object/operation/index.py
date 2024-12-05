from base.locator import Locator
from base.element import Page


class Index:
    def __init__(self):
        self.page = Page().load().index

    # 启动首页
    def launch_index(self, url):
        Locator().goto(url)

    # 用户名输入
    def username_input(self, username):
        Locator(self.page.user_text).input(username)

    # 密码输入
    def password_input(self, password):
        Locator(self.page.password_text).input(password)

    # 登录确认
    def click_confirm(self):
        Locator(self.page.confirm_button).click()

    # 获取登录提示文本
    def get_login_tip(self):
        return Locator(self.page.login_tip).get_text()
