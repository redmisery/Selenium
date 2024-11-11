from base.driver import Driver
from base.locator import Locator


class Index:
    # 公用字段
    # 浏览器最大化
    driver = Driver().driver
    # 元素
    # 用户名
    user_text = {'xpath': '//*[@id="login"]/div/span[1]/input'}
    # 密码
    password_text = {'css': '#login > div > span.ant-input-affix-wrapper.ant-input-password.input___3_OCv > input'}
    # 确认键
    confirm_button = {'css': '#login > div > button'}
    # 登录提示
    login_tip = {'xpath': "//div[contains(@class,'ant-message-custom-content')]/span[2]"}

    # 元素操作

    # 启动首页
    def launch_index(self, url):
        Locator(self.driver).goto(url)

    # 用户名输入
    def username_input(self, username):
        Locator(self.driver, self.user_text).send_keys(username)

    # 密码输入
    def password_input(self, password):
        Locator(self.driver, self.password_text).send_keys(password)

    # 登录确认
    def click_confirm(self):
        Locator(self.driver, self.confirm_button).click()

    # 获取登录提示文本
    def get_login_tip(self):
        return Locator(self.driver, self.login_tip).get_text()
