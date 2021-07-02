# -*- coding: utf-8 -*-
import abc
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field
from YiriMirai.models.base import MiraiBaseModel


class Entity(MiraiBaseModel):
    '''实体，表示一个用户或群。'''
    def __repr__(self):
        return f'<{self.__class__.__name__} {str(self)}>'

    @abc.abstractmethod
    def get_avatar_url(self) -> str:
        pass


class Friend(Entity):
    '''好友。'''
    id: int
    nickname: Optional[str]
    remark: Optional[str]

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Permission(str, Enum):
    '''群成员身份权限。'''
    Member = "MEMBER"
    Administrator = "ADMINISTRATOR"
    Owner = "OWNER"


class Group(Entity):
    '''群。'''
    id: int
    name: str
    permission: Permission

    def get_avatar_url(self) -> str:
        return f'https://p.qlogo.cn/gh/{self.id}/{self.id}/'


class GroupMember(Entity):
    '''群成员。'''
    id: int
    member_name: str = Field(..., alias='memberName')
    permission: Permission
    group: Group
    special_title: str = Field('', alias='specialTitle')
    join_timestamp: datetime = Field(0, alias='joinTimestamp')
    last_speak_timestamp: datetime = Field(0, alias='lastSpeakTimestamp')
    mute_time_remaining: int = Field(0, alias='muteTimeRemaining')

    def __repr__(self):
        return f"<GroupMember id={self.id} group={self.group} permission={self.permission} group={self.group.id}>"

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Sender(Entity):
    '''来自其他客户端的用户。'''
    id: int
    platform: str

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Config(MiraiBaseModel):
    '''配置项类型。'''
    def modify(self, **kwargs) -> 'Config':
        '''修改部分设置。'''
        for k, v in kwargs.items():
            if k in self.__fields__:
                setattr(self, k, v)
            else:
                raise ValueError(f'未知配置项: {k}')
        return self


class GroupConfig(Config):
    '''群配置。'''
    name: str
    announcement: str
    confess_talk: bool = Field(..., alias='confessTalk')
    allow_member_invite: bool = Field(..., alias='allowMemberInvite')
    auto_approve: bool = Field(..., alias='autoApprove')
    anonymous_chat: bool = Field(..., alias='anonymousChat')


class MemberInfo(Config, GroupMember):
    '''群成员信息。'''


__all__ = [
    'Entity',
    'Friend',
    'Group',
    'GroupMember',
    'Permission',
    'Sender',
]
