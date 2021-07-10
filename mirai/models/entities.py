# -*- coding: utf-8 -*-
"""
此模块提供实体和配置项模型。
"""
import abc
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field
from mirai.models.base import MiraiBaseModel


class Entity(MiraiBaseModel):
    """实体，表示一个用户或群。"""
    def __repr__(self):
        return f'<{self.__class__.__name__} {str(self)}>'

    @abc.abstractmethod
    def get_avatar_url(self) -> str:
        """获取头像图片链接。"""
        pass


class Friend(Entity):
    """好友。"""
    id: int
    """QQ 号。"""
    nickname: Optional[str]
    """昵称。"""
    remark: Optional[str]
    """备注。"""
    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Permission(str, Enum):
    """群成员身份权限。"""
    Member = "MEMBER"
    """成员。"""
    Administrator = "ADMINISTRATOR"
    """管理员。"""
    Owner = "OWNER"
    """群主。"""


class Group(Entity):
    """群。"""
    id: int
    """群号。"""
    name: str
    """群名称。"""
    permission: Permission
    """Bot 在群中的权限。"""
    def get_avatar_url(self) -> str:
        return f'https://p.qlogo.cn/gh/{self.id}/{self.id}/'


class GroupMember(Entity):
    """群成员。"""
    id: int
    """QQ 号。"""
    member_name: str
    """群成员名称。"""
    permission: Permission
    """Bot 在群中的权限。"""
    group: Group
    """群。"""
    special_title: str = ''
    """群头衔。"""
    join_timestamp: datetime = 0
    """加入群的时间。"""
    last_speak_timestamp: datetime = 0
    """最后一次发言的时间。"""
    mute_time_remaining: int = 0
    """禁言剩余时间。"""
    def __repr__(self):
        return f"<GroupMember id={self.id} group={self.group} permission={self.permission} group={self.group.id}>"

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Sender(Entity):
    """来自其他客户端的用户。"""
    id: int
    """QQ 号。"""
    platform: str
    """来源平台。"""
    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Config(MiraiBaseModel):
    """配置项类型。"""
    def modify(self, **kwargs) -> 'Config':
        """修改部分设置。"""
        for k, v in kwargs.items():
            if k in self.__fields__:
                setattr(self, k, v)
            else:
                raise ValueError(f'未知配置项: {k}')
        return self


class GroupConfig(Config):
    """群配置。"""
    name: str
    """群名称。"""
    announcement: str
    """群公告。"""
    confess_talk: bool
    """是否允许坦白说。"""
    allow_member_invite: bool
    """是否允许成员邀请好友入群。"""
    auto_approve: bool
    """是否开启自动审批入群。"""
    anonymous_chat: bool
    """是否开启匿名聊天。"""


class MemberInfo(Config, GroupMember):
    """群成员信息。"""


__all__ = [
    'Entity',
    'Friend',
    'Group',
    'GroupMember',
    'Permission',
    'Sender',
    'Config',
    'GroupConfig',
    'MemberInfo',
]
