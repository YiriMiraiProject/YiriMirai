# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from typing import Optional, Type

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import BaseModel, Field
from YiriMirai.models.entities import (
    Friend, Group, GroupMember, GroupMemberEx, Permission, Sender
)
from YiriMirai.models.message import MessageChain


class Event(BaseModel):
    '''事件基类。'''
    type: str

    class Config:
        extra = 'allow'
        allow_population_by_field_name = True

    @classmethod
    def get_subtype(cls, name: str) -> Type['Event']:
        '''根据类名称，获取相应的子类类型。'''
        try:
            type_ = getattr(sys.modules[__name__], name)
            if not issubclass(type_, cls):
                raise ValueError(f'`{name}`不是`{cls.__name__}`的子类！')
            return type_
        except AttributeError as e:
            raise ValueError(f'`{name}`不是`{cls.__name__}`的子类！') from e

    @classmethod
    def parse_obj(cls, event: dict):
        '''通过 mirai-api-http 发回的事件，构造对应的 Event 对象。
        `event: dict` 已解析的事件 JSON
        '''
        if cls == Event:
            EventType = cls.get_subtype(event['type'])
            return EventType.parse_obj(event)
        else:
            return super().parse_obj(event)


###############################
# Bot Event
class BotEvent(Event):
    '''Bot 自身事件。'''
    qq: int


class BotOnlineEvent(BotEvent):
    '''Bot 登陆成功。'''
    type: str = 'BotOnlineEvent'


class BotOfflineEventActive(BotEvent):
    '''Bot 主动离线。'''
    type: str = 'BotOfflineEventActive'


class BotOfflineEventForce(BotEvent):
    '''Bot被挤下线。'''
    type: str = 'BotOfflineEventForce'


class BotOfflineEventDropped(BotEvent):
    '''Bot 被服务器断开或因网络问题而掉线。'''
    type: str = 'BotOfflineEventDropped'


class BotReloginEvent(BotEvent):
    '''Bot 主动重新登录。'''
    type: str = 'BotReloginEvent'


###############################
# Friend Event


class FriendEvent(Event):
    '''好友事件。'''
    friend: Friend


class FriendInputStatusChangedEvent(FriendEvent):
    '''好友输入状态改变。'''
    type: str = 'FriendInputStatusChangedEvent'
    inputting: bool


class FriendNickChangedEvent(FriendEvent):
    '''好友昵称改变。'''
    type: str = 'FriendNickChangedEvent'
    from_: str = Field(..., alias="from")
    to: str


###############################
# Group Event


class GroupEvent(Event):
    '''群事件。'''
    # group: Group
    # 一个奇怪的现象：群事件不一定有 group，它可能藏在 opeartor.group 里


class BotGroupPermissionChangeEvent(GroupEvent):
    ''' Bot在群里的权限被改变。'''
    type: str = 'BotGroupPermissionChangeEvent'
    origin: Permission
    current: Permission
    group: Group


class BotMuteEvent(GroupEvent):
    '''Bot 被禁言。'''
    type: str = 'BotMuteEvent'
    durationSeconds: int
    operator: Optional[GroupMemberEx]


class BotUnmuteEvent(GroupEvent):
    '''Bot 被取消禁言。'''
    type: str = 'BotUnmuteEvent'
    operator: Optional[GroupMemberEx]


class BotJoinGroupEvent(GroupEvent):
    '''Bot 加入了一个新群。'''
    type: str = 'BotJoinGroupEvent'
    group: Group


class BotLeaveEventActive(GroupEvent):
    '''Bot 主动退出一个群。'''
    type: str = 'BotLeaveEventActive'
    group: Group


class BotLeaveEventKick(GroupEvent):
    '''Bot 被踢出一个群。'''
    type: str = 'BotLeaveEventKick'
    group: Group


class GroupRecallEvent(GroupEvent):
    '''群消息撤回。'''
    type: str = 'GroupRecallEvent'
    authorId: int
    messageId: int
    time: datetime
    group: Group
    operator: Optional[GroupMemberEx]


class FriendRecallEvent(Event):
    '''好友消息撤回。'''
    type: str = 'FriendRecallEvent'
    # 按照文档顺序，这个事件确实应该在这个位置。
    # 而且它不符合 FriendEvent 的形式，就放在这里吧。
    authorId: int
    messageId: int
    time: int
    operator: int


class GroupNameChangeEvent(GroupEvent):
    '''某个群名改变。'''
    type: str = 'GroupNameChangeEvent'
    origin: str
    current: str
    group: Group
    operator: Optional[GroupMemberEx]


class GroupEntranceAnnouncementChangeEvent(GroupEvent):
    '''某群入群公告改变。'''
    type: str = 'GroupEntranceAnnouncementChangeEvent'
    origin: str
    current: str
    group: Group
    operator: Optional[GroupMemberEx]


class GroupMuteAllEvent(GroupEvent):
    '''全员禁言。'''
    type: str = 'GroupMuteAllEvent'
    origin: bool
    current: bool
    group: Group
    operator: Optional[GroupMemberEx]


class GroupAllowAnonymousChatEvent(GroupEvent):
    '''匿名聊天。'''
    type: str = 'GroupAllowAnonymousChatEvent'
    origin: bool
    current: bool
    group: Group
    operator: Optional[GroupMember]


class GroupAllowConfessTalkEvent(GroupEvent):
    '''坦白说。'''
    type: str = 'GroupAllowConfessTalkEvent'
    origin: bool
    current: bool
    group: Group
    isByBot: bool


class GroupAllowMemberInviteEvent(GroupEvent):
    '''允许群员邀请好友加群。'''
    type: str = 'GroupAllowMemberInviteEvent'
    origin: bool
    current: bool
    group: Group
    operator: Optional[GroupMemberEx]


class MemberJoinEvent(GroupEvent):
    '''新人入群。'''
    type: str = 'MemberJoinEvent'
    member: GroupMemberEx


class MemberLeaveEventKick(GroupEvent):
    '''成员被踢出群（该成员不是Bot）。'''
    type: str = 'MemberLeaveEventKick'
    member: GroupMemberEx
    operator: Optional[GroupMemberEx]


class MemberLeaveEventQuit(GroupEvent):
    '''成员主动离群（该成员不是Bot）。'''
    type: str = 'MemberLeaveEventQuit'
    member: GroupMember


class MemberCardChangeEvent(GroupEvent):
    '''群名片改动。'''
    type: str = 'MemberCardChangeEvent'
    origin: str
    current: str
    member: GroupMemberEx


class MemberSpecialTitleChangeEvent(GroupEvent):
    '''群头衔改动（只有群主有操作权限）。'''
    type: str = 'MemberSpecialTitleChangeEvent'
    origin: str
    current: str
    member: GroupMember


class MemberPermissionChangeEvent(GroupEvent):
    '''成员权限改变（该成员不是Bot）。'''
    type: str = 'MemberPermissionChangeEvent'
    origin: str
    current: str
    member: GroupMember


class MemberMuteEvent(GroupEvent):
    '''群成员被禁言（该成员不是Bot）。'''
    type: str = 'MemberMuteEvent'
    durationSeconds: int


class MemberUnmuteEvent(GroupEvent):
    '''群成员被取消禁言（该成员不是Bot）。'''
    type: str = 'MemberUnmuteEvent'
    member: GroupMember
    operator: Optional[GroupMemberEx]


class MemberHonorChangeEvent(GroupEvent):
    '''群员称号改变。'''
    type: str = 'MemberHonorChangeEvent'
    member: GroupMemberEx
    action: Literal['achieve', 'lose']
    honor: str


###############################
# Request Event


class RequestEvent(Event):
    '''申请事件。'''
    event_id: int = Field(..., alias='eventId')


class NewFriendRequestEvent(RequestEvent):
    '''添加好友申请。'''
    type: str = 'NewFriendRequestEvent'
    from_id: int = Field(..., alias='fromId')
    group_id: int = Field(..., alias='groupId')
    nick: str
    message: str


class MemberJoinRequestEvent(RequestEvent):
    '''用户入群申请（Bot需要有管理员权限）。'''
    type: str = 'MemberJoinRequestEvent'
    from_id: int = Field(..., alias='fromId')
    group_id: int = Field(..., alias='groupId')
    group_name: str = Field(..., alias='groupName')
    nick: str
    message: str


class BotInvitedJoinGroupRequestEvent(RequestEvent):
    '''Bot 被邀请入群申请。'''
    type: str = 'BotInvitedJoinGroupRequestEvent'
    from_id: int = Field(..., alias='fromId')
    group_id: int = Field(..., alias='groupId')
    group_name: str = Field(..., alias='groupName')
    nick: str
    message: str


###############################
# Command Event


class CommandEvent(Event):
    '''命令事件。'''


class CommandExecutedEvent(CommandEvent):
    type: str = 'CommandExecutedEvent'
    name: str
    friend: Optional[Friend]
    member: Optional[GroupMember]
    args: MessageChain


###############################
# Message Event
class MessageEvent(Event):
    '''消息事件。'''
    message_chain: MessageChain = Field(..., alias='messageChain')


class FriendMessage(MessageEvent):
    '''好友消息'''
    type: str = 'FriendMessage'
    sender: Friend


class GroupMessage(MessageEvent):
    '''群消息。'''
    type: str = 'GroupMessage'
    sender: GroupMemberEx


class TempMessage(MessageEvent):
    '''群临时消息。'''
    type: str = 'TempMessage'
    sender: GroupMemberEx


class StrangerMessage(MessageEvent):
    '''陌生人消息。'''
    type: str = 'StrangerMessage'
    sender: Friend


class OtherClientMessage(MessageEvent):
    '''其他客户端消息。'''
    type: str = 'OtherClientMessage'
    sender: Sender


__all__ = [
    'BotEvent',
    'BotGroupPermissionChangeEvent',
    'BotInvitedJoinGroupRequestEvent',
    'BotJoinGroupEvent',
    'BotLeaveEventActive',
    'BotLeaveEventKick',
    'BotMuteEvent',
    'BotOfflineEventActive',
    'BotOfflineEventDropped',
    'BotOfflineEventForce',
    'BotOnlineEvent',
    'BotReloginEvent',
    'BotUnmuteEvent',
    'CommandEvent',
    'CommandExecutedEvent',
    'Event',
    'FriendEvent',
    'FriendInputStatusChangedEvent',
    'FriendMessage',
    'FriendNickChangedEvent',
    'FriendRecallEvent',
    'GroupAllowAnonymousChatEvent',
    'GroupAllowConfessTalkEvent',
    'GroupAllowMemberInviteEvent',
    'GroupEntranceAnnouncementChangeEvent',
    'GroupEvent',
    'GroupMember',
    'GroupMemberEx',
    'GroupMessage',
    'GroupMuteAllEvent',
    'GroupNameChangeEvent',
    'GroupRecallEvent',
    'MemberCardChangeEvent',
    'MemberHonorChangeEvent',
    'MemberJoinEvent',
    'MemberJoinRequestEvent',
    'MemberLeaveEventKick',
    'MemberLeaveEventQuit',
    'MemberMuteEvent',
    'MemberPermissionChangeEvent',
    'MemberSpecialTitleChangeEvent',
    'MemberUnmuteEvent',
    'MessageEvent',
    'NewFriendRequestEvent',
    'OtherClientMessage',
    'RequestEvent',
    'StrangerMessage',
    'TempMessage',
]
