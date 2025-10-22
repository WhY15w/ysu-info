from .YsuInfo import pushScore
from .YsuInfo import pushGPA_offline
from .YsuInfo import pushGPA_online
from nonebot import on_command
from nonebot.typing import T_State
import asyncio
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    Event,
)

ysu_gpa = on_command("ysu_gpa", aliases={"绩点", "GPA"}, priority=5)


@ysu_gpa.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await ysu_gpa.finish(pushGPA_offline())
