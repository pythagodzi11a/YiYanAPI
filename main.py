from pathlib import Path

import requests
import toml
from ncatbot.core import GroupMessage, PrivateMessage
from ncatbot.plugin import BasePlugin, CompatibleEnrollment


class Config:
    def __init__(self, raw_info: dict):
        private_config = raw_info.get("private", {})
        group_config = raw_info.get("group", {})

        self.private_enabled = private_config["enable"]
        self.group_enabled = group_config["enable"]

        self.group_mode = group_config["mode"]
        self.private_mode = private_config["mode"]
        self.private_black_lists = private_config["blacklist"]
        self.group_black_lists = group_config["blacklist"]
        self.private_white_lists = private_config["whitelist"]
        self.group_white_lists = group_config["whitelist"]

    def should_process_group(self, group_id: str) -> bool:
        """

        :param group_id:
        :return:
        """
        if self.group_enabled:
            if self.group_mode == "blacklist":
                return False if group_id in self.group_black_lists else True
            else:
                return True if group_id in self.group_white_lists else False
        else:
            return False

    def should_process_private(self, user_id: str) -> bool:
        """

        :param user_id:
        :return:
        """
        if self.private_enabled:
            if self.private_mode == "blacklist":
                return False if user_id in self.private_black_lists else True
            else:
                return True if user_id in self.private_white_lists else False
        else:
            return False

    # plugin = raw_info.get("plugin", {})
    # self.mode = plugin.get("mode", "blacklist")
    # lists = plugin.get("lists", {})
    #
    # self.blacklists = lists.get("blacklist", [])
    # self.whitelists = lists.get("whitelist", [])


config_path = Path(__file__).parent / "config.toml"
with open(config_path, "r", encoding="utf-8") as config_file:
    config = Config(toml.load(config_file))
bot = CompatibleEnrollment  # 兼容回调函数注册器


class YiYanAPI(BasePlugin):
    name = "YiYanAPI"  # 插件名称
    version = "0.0.2"  # 插件版本
    author = "pythagodzilla"  # 插件作者
    description = "每日一言"  # 插件描述

    @bot.private_event()
    async def on_message(self, msg: PrivateMessage):
        if config.should_process_private(msg.user_id):
            if msg.message[0]["type"] == "text":
                if msg.raw_message == "一言":
                    content = requests.get("https://v1.hitokoto.cn/?c=f&encode=text").text

                    await self.api.post_private_msg(msg.user_id, content)

    @bot.group_event()
    async def on_message(self, msg: GroupMessage):
        if config.should_process_group(msg.group_id):
            if msg.message[0]["type"] == "text":
                if msg.raw_message == "一言":
                    content = requests.get("https://v1.hitokoto.cn/?c=f&encode=text").text

                    await self.api.post_group_msg(msg.group_id, content)
