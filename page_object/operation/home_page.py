from base import Locator
from base.element import Page


class HomePage:
    def __init__(self):
        # 首页
        self.page = Page().load()

    def get_version_info(self) -> str:
        """
        获取版本信息
        :return: 版本信息
        """
        page = self.page
        Locator(page.version_information).click()
        return Locator(page.version_number).get_text()

    def open_settings(self):
        """
        打开设置页面
        """
        Locator(self.page.settings).click()

    class SoftwareName:
        def __init__(self):
            # software模块
            self.page = Page().load().software

        def modify_software_name(self, new_name):
            """
            修改平台名称
            :param new_name:新平台名称
            """
            page = self.page
            Locator(page.software_name).double_click()
            Locator(page.software_name_input).input(new_name)
            Locator(page.software_name_confirm).click()

        def get_software_name(self) -> str:
            """
            获取平台名称
            :return: 平台名称
            """
            page = self.page
            return Locator(page.software_name).get_text()

        def restore_software_name(self):
            """
            还原平台名称
            """
            original_name = "视频轨迹跟踪平台软件"
            self.modify_software_name(original_name)

    class User:
        def __init__(self):
            # 用户模块
            self.page = Page().load().user

        def change_password(self, old_password, new_password):
            """
            修改密码
            :param old_password: 旧密码
            :param new_password: 新密码
            """
            Locator(self.page.user).hover()
            Locator(self.page.modify_password).click()
            Locator(self.page.old_password_input).input(old_password)
            Locator(self.page.new_password_input).input(new_password)
            Locator(self.page.confirm_password_input).input(new_password)
            Locator(self.page.confirm_password_change).click()

        def get_password_tip(self) -> str:
            """
            获取密码弹窗提示信息
            :return: 密码弹窗提示信息
            """
            return Locator(self.page.pop_tips).get_text()

        def get_password_format_tip(self) -> str:
            """
            获取密码格式提示
            :return: 密码格式提示
            """
            return Locator(self.page.password_format_tip).get_text()

        def logout(self):
            """
            退出登录
            """
            Locator(self.page.logout).click()
