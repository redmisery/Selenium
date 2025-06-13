# -*- encoding: utf8 -*-
__author__ = "admin"

from airtest.core.api import *
from airtest.cli.parser import cli_setup
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import time


class AirtestAutomation:
    def __init__(self):
        self.poco = None
        self.operation_steps = [
            {"name": "步骤1", "template": "tpl1741769579558.png", "pos": (0.015, 0.061), "delay": 5},  # 点击首页视频询问
            #             {"name": "步骤2", "template": "tpl1741930259997.png", "pos": (0.099, -0.19), "delay": 5},  #点击视频询问模块
            {"name": "步骤8", "template": "tpl1742174532268.png", "pos": (0.457, -0.246), "delay": 5},  # 返回首页
            {"name": "步骤9", "template": "tpl1742174537362.png", "pos": (0.068, 0.032), "delay": 5}  # 确定
            #             {"name": "步骤3", "template": "tpl1741769586324.png", "pos": (0.417, -0.026), "delay": 5},  #进入视频询问模版
            #             {"name": "步骤4", "template": "tpl1741769590004.png", "pos": (0.255, 0.243), "delay": 1500},   #开始问答
            #             {"name": "步骤5", "template": "tpl1741769841962.png", "pos": (0.414, 0.229), "delay": 5},   #结束问答
            #             {"name": "步骤6", "template": "tpl1741849938734.png", "pos": (-0.031, 0.044), "delay": 5},  #确定
            #             {"name": "步骤7", "template": "tpl1741846444569.png", "pos": (0.448, 0.231), "delay": 10}    #完成并上传
        ]

    def initialize(self):
        """初始化设备连接"""
        if not cli_setup():
            auto_setup(
                __file__,
                logdir=True,
                devices=["android://127.0.0.1:5037/SZKDR0000002?touch_method=MAXTOUCH&"]
            )
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

    def execute_step(self, step_config, attempt=1):
        """执行单个步骤带错误处理"""
        try:
            print(f"执行 {step_config['name']} [尝试{attempt}]")
            template = Template(
                r"{}".format(step_config["template"]),
                record_pos=step_config["pos"],
                resolution=(1920, 1080)
            )
            touch(template)
            if not exists(template):
                raise Exception("元素未成功触发")
            time.sleep(step_config["delay"])
            return True
        except Exception as e:
            print(f"{step_config['name']} 执行失败: {str(e)}")
            return False

    def execute_recovery_actions(self):
        """执行异常恢复操作"""
        recovery_steps = [
            {"name": "恢复步骤1", "template": "tpl1742174532268.png", "pos": (0.457, -0.246), "delay": 5},  # 返回首页
            {"name": "恢复步骤2", "template": "tpl1742174537362.png", "pos": (0.068, 0.032), "delay": 5}  # 确定
        ]

        print("正在执行异常恢复操作...")
        for step in recovery_steps:
            try:
                if exists(Template(step["template"]), record_pos=step["pos"], resolution=(1920, 1080)):
                    touch(step["pos"])
                time.sleep(step["delay"])
            except Exception as e:
                print(f"恢复操作 {step['name']} 执行失败: {str(e)}")
                break  # def execute_recovery_actions(self):

    def run_cycle(self, cycle_times=3, retries=3):
        """执行完整循环流程"""
        for cycle in range(1, cycle_times + 1):
            print(f"\n======== 开始第 {cycle}/{cycle_times} 次循环 ========")
            for step in self.operation_steps:
                success = False
                for attempt in range(1, retries + 1):
                    if self.execute_step(step, attempt):
                        success = True
                        break
                if not success:
                    self.execute_recovery_actions()
                    print(f"!! {step['name']} 重试{retries}次后仍失败，终止流程")
                    return False
            self._reset_status()  # 每次循环后重置状态
        return True


#     def _reset_status(self):
#         """重置应用状态（根据实际需求实现）"""
#         print("正在重置应用状态...")
#         # 示例：按返回键回到主页
#         keyevent("BACK")
#         time.sleep(2)

if __name__ == "__main__":
    automator = AirtestAutomation()
    automator.initialize()

    try:
        result = automator.run_cycle(
            cycle_times=200,  # 设置循环次数
            retries=1  # 每个步骤的重试次数
        )
        print(f"\n最终执行结果: {'成功' if result else '失败'}")
    except Exception as e:
        print(f"发生未捕获的异常: {str(e)}")
    finally:
        print("自动化流程执行结束")
