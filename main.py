from pathlib import Path

import aiohttp
import toml
from ncatbot.core import GroupMessage, PrivateMessage
from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.utils import get_log

_log = get_log()


class Config:
    def __init__(self):

        config_path = Path(__file__).parent / "config.toml"
        with open(config_path, "r", encoding="utf-8") as config_file:
            raw_info = toml.load(config_file)

        private_config = raw_info.get("private", {})
        group_config = raw_info.get("group", {})

        self.private_enabled = private_config.get("enable", False)
        self.group_enabled = group_config.get("enable", False)

        self.group_mode = group_config.get("mode")
        self.private_mode = private_config.get("mode")
        self.private_black_lists = private_config.get("blacklist")
        self.group_black_lists = group_config.get("blacklist")
        self.private_white_lists = private_config.get("whitelist")
        self.group_white_lists = group_config.get("whitelist")

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


config = Config()
bot = CompatibleEnrollment  # 兼容回调函数注册器


class YiYanAPI(BasePlugin):
    name = "YiYanAPI"  # 插件名称
    version = "0.1.0"  # 插件版本
    author = "pythagodzilla"  # 插件作者
    description = "每日一言"  # 插件描述

    @bot.private_event()
    async def on_message(self, msg: PrivateMessage):
        if config.should_process_private(msg.user_id):
            if msg.message[0]["type"] == "text":
                if msg.raw_message == "一言":
                    content = await self.fetch_yiyan()

                    await self.api.post_private_msg(msg.user_id, content)

    @bot.group_event()
    async def on_message(self, msg: GroupMessage):
        if config.should_process_group(msg.group_id):
            if msg.message[0]["type"] == "text":
                if msg.raw_message == "一言":
                    content = await self.fetch_yiyan()

                    await self.api.post_group_msg(msg.group_id, content)

    @staticmethod
    async def fetch_yiyan() -> str:
        url = "https://v1.hitokoto.cn/?c=f&encode=text"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
        }
        # noinspection PyBroadException
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()

        except Exception as e:
            _log.error(e)
            return "获取一言失败啦！联系机器人管理员上门维修吧！"
