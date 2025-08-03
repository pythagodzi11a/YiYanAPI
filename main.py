import requests
from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core import GroupMessage, PrivateMessage

bot = CompatibleEnrollment  # 兼容回调函数注册器


class YiYanAPI(BasePlugin):
    name = "YiYanAPI"  # 插件名称
    version = "0.0.1"  # 插件版本
    author = "pythagodzilla"  # 插件作者
    info = "每日一言"  # 插件描述

    @bot.private_event()
    async def on_message(self, msg: PrivateMessage):
        if msg.message[0]["type"] == "text":
            if msg.raw_message == "一言":
                content = requests.get("https://v1.hitokoto.cn/?c=f&encode=text").text

                await self.api.post_private_msg(msg.user_id, content)

    @bot.group_event()
    async def on_message(self, msg: GroupMessage):
        if msg.message[0]["type"] == "text":
            if msg.raw_message == "一言":
                content = requests.get("https://v1.hitokoto.cn/?c=f&encode=text").text

                await self.api.post_group_msg(msg.group_id, content)
