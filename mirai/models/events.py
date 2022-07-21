# -*- coding: utf-8 -*-
"""
此模块提供事件模型。
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, cast

if TYPE_CHECKING:
    from typing_extensions import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal

from mirai.models.base import MiraiIndexedMetaclass, MiraiIndexedModel
from mirai.models.entities import (Client, Entity, Friend, Group, GroupMember,
                                   Permission, Subject)
from mirai.models.message import MessageChain

TEventClass = TypeVar("TEventClass", bound='EventMetaclass')


class EventMetaclass(MiraiIndexedMetaclass):
    def get_subtype(cls: TEventClass, name: str) -> TEventClass:
        try:
            return super().get_subtype(name)
        except ValueError:
            return cast(TEventClass, Event)


class Event(MiraiIndexedModel, metaclass=EventMetaclass):
    """事件基类。

    Args:
        type: 事件名。
    """
    type: str
    """事件名。"""
    def __repr_args__(self):
        return [(k, v) for k, v in self.__dict__.items() if k != 'type' and v]

    @classmethod
    def parse_subtype(cls, obj: dict) -> 'Event':
        try:
            return cast(Event, super().parse_subtype(obj))
        except ValueError:
            return Event(**obj)


###############################
# Bot Event
class BotEvent(Event):
    """Bot 自身事件。

    Args:
        type: 事件名。
        qq: Bot 的 QQ 号。
    """
    type: str
    """事件名。"""
    qq: int
    """Bot 的 QQ 号。"""


class BotOnlineEvent(BotEvent):
    """Bot 登陆成功。

    Args:
        type: 事件名。
        qq: 登陆成功的 Bot 的 QQ 号。
    """
    type: str = 'BotOnlineEvent'
    """事件名。"""
    qq: int
    """登陆成功的 Bot 的 QQ 号。"""


class BotOfflineEventActive(BotEvent):
    """Bot 主动离线。

    Args:
        type: 事件名。
        qq: 主动离线的 Bot 的 QQ 号。
    """
    type: str = 'BotOfflineEventActive'
    """事件名。"""
    qq: int
    """主动离线的 Bot 的 QQ 号。"""


class BotOfflineEventForce(BotEvent):
    """Bot被挤下线。

    Args:
        type: 事件名。
        qq: 被挤下线的 Bot 的 QQ 号。
    """
    type: str = 'BotOfflineEventForce'
    """事件名。"""
    qq: int
    """被挤下线的 Bot 的 QQ 号。"""


class BotOfflineEventDropped(BotEvent):
    """Bot 被服务器断开或因网络问题而掉线。

    Args:
        type: 事件名。
        qq: 被服务器断开或因网络问题而掉线的 Bot 的 QQ 号。
    """
    type: str = 'BotOfflineEventDropped'
    """事件名。"""
    qq: int
    """被服务器断开或因网络问题而掉线的 Bot 的 QQ 号。"""


class BotReloginEvent(BotEvent):
    """Bot 主动重新登录。

    Args:
        type: 事件名。
        qq: 主动重新登录的 Bot 的 QQ 号。
    """
    type: str = 'BotReloginEvent'
    """事件名。"""
    qq: int
    """主动重新登录的 Bot 的 QQ 号。"""


###############################
# Friend Event


class FriendEvent(Event):
    """好友事件。

    Args:
        type: 事件名。
        friend: 事件对应的好友。
    """
    type: str
    """事件名。"""
    friend: Friend
    """事件对应的好友。"""


class FriendInputStatusChangedEvent(FriendEvent):
    """好友输入状态改变。

    Args:
        type: 事件名。
        friend: 事件对应的好友。
        inputting: 是否正在输入。
    """
    type: str = 'FriendInputStatusChangedEvent'
    """事件名。"""
    friend: Friend
    """事件对应的好友。"""
    inputting: bool
    """是否正在输入。"""


class FriendNickChangedEvent(FriendEvent):
    """好友昵称改变。

    Args:
        type: 事件名。
        friend: 事件对应的好友。
        from_: 原昵称。
        to: 新昵称。
    """
    type: str = 'FriendNickChangedEvent'
    """事件名。"""
    friend: Friend
    """事件对应的好友。"""
    from_: str
    """原昵称。"""
    to: str
    """新昵称。"""


###############################
# Group Event


class GroupEvent(Event):
    """群事件。

    Args:
        type: 事件名。
        group: 事件对应的群。
    """
    # group: Group
    # 一个奇怪的现象：群事件不一定有 group，它可能藏在 operator.group 里

    type: str
    """事件名。"""
    def __getattr__(self, name) -> Union[Group, Any]:
        if name == 'group':
            member = getattr(self, 'operator',
                             None) or getattr(self, 'member', None)
            if member:
                return member.group
        return getattr(super(), name)


class BotGroupPermissionChangeEvent(GroupEvent):
    """ Bot在群里的权限被改变。

    Args:
        type: 事件名。
        origin: 原权限。
        current: 新权限。
        group: 事件对应的群。
    """
    type: str = 'BotGroupPermissionChangeEvent'
    """事件名。"""
    origin: Permission
    """原权限。"""
    current: Permission
    """新权限。"""
    group: Group
    """事件对应的群。"""


class BotMuteEvent(GroupEvent):
    """Bot 被禁言。

    Args:
        type: 事件名。
        duration_seconds: 禁言时间，单位秒。
        operator: 禁言的操作者。
    """
    type: str = 'BotMuteEvent'
    """事件名。"""
    duration_seconds: int
    """禁言时间，单位秒。"""
    operator: Optional[GroupMember]
    """禁言的操作者。"""


class BotUnmuteEvent(GroupEvent):
    """Bot 被取消禁言。

    Args:
        type: 事件名。
        operator: 取消禁言的操作者。
    """
    type: str = 'BotUnmuteEvent'
    """事件名。"""
    operator: Optional[GroupMember]
    """取消禁言的操作者。"""


class BotJoinGroupEvent(GroupEvent):
    """Bot 加入了一个新群。

    Args:
        type: 事件名。
        group: Bot 加入的群。
    """
    type: str = 'BotJoinGroupEvent'
    """事件名。"""
    group: Group
    """Bot 加入的群。"""
    invitor: Optional[GroupMember] = None
    """邀请者。"""


class BotLeaveEventActive(GroupEvent):
    """Bot 主动退出一个群。

    Args:
        type: 事件名。
        group: Bot 退出的群。
    """
    type: str = 'BotLeaveEventActive'
    """事件名。"""
    group: Group
    """Bot 退出的群。"""


class BotLeaveEventKick(GroupEvent):
    """Bot 被踢出一个群。

    Args:
        type: 事件名。
        group: Bot 被踢出的群。
    """
    type: str = 'BotLeaveEventKick'
    """事件名。"""
    group: Group
    """Bot 被踢出的群。"""
    operator: Optional[GroupMember]
    """踢出 Bot 的管理员。"""


class GroupRecallEvent(GroupEvent):
    """群消息撤回。

    Args:
        type: 事件名。
        author_id: 原消息发送者的 QQ 号。
        message_id: 原消息 message_id。
        time: 原消息发送时间。
        group: 消息撤回所在的群。
        operator: 消息撤回的操作者，为 None 表示 Bot 操作。
    """
    type: str = 'GroupRecallEvent'
    """事件名。"""
    author_id: int
    """原消息发送者的 QQ 号。"""
    message_id: int
    """原消息 message_id。"""
    time: datetime
    """原消息发送时间。"""
    group: Group
    """消息撤回所在的群。"""
    operator: Optional[GroupMember]
    """消息撤回的操作者，为 None 表示 Bot 操作。"""


class FriendRecallEvent(Event):
    """好友消息撤回。

    Args:
        type: 事件名。
        author_id: 原消息发送者的 QQ 号。
        message_id: 原消息 message_id。
        time: 原消息发送时间。
        operator: 好友 QQ 号或 Bot QQ 号。
    """
    type: str = 'FriendRecallEvent'
    """事件名。"""
    # 按照文档顺序，这个事件确实应该在这个位置。
    # 而且它不符合 FriendEvent 的形式，就放在这里吧。
    author_id: int
    """原消息发送者的 QQ 号。"""
    message_id: int
    """原消息 message_id。"""
    time: datetime
    """原消息发送时间。"""
    operator: int
    """好友 QQ 号或 Bot QQ 号。"""


class GroupNameChangeEvent(GroupEvent):
    """某个群名改变。

    Args:
        type: 事件名。
        origin: 原群名。
        current: 新群名。
        group: 群名改名的群。
        operator: 操作者，为 None 表示 Bot 操作。
    """
    type: str = 'GroupNameChangeEvent'
    """事件名。"""
    origin: str
    """原群名。"""
    current: str
    """新群名。"""
    group: Group
    """群名改名的群。"""
    operator: Optional[GroupMember]
    """操作者，为 None 表示 Bot 操作。"""


class GroupEntranceAnnouncementChangeEvent(GroupEvent):
    """某群入群公告改变。

    Args:
        type: 事件名。
        origin: 原公告。
        current: 新公告。
        group: 群公告改变的群。
        operator: 操作者，为 None 表示 Bot 操作。
    """
    type: str = 'GroupEntranceAnnouncementChangeEvent'
    """事件名。"""
    origin: str
    """原公告。"""
    current: str
    """新公告。"""
    group: Group
    """群公告改变的群。"""
    operator: Optional[GroupMember]
    """操作者，为 None 表示 Bot 操作。"""


class GroupMuteAllEvent(GroupEvent):
    """全员禁言。

    Args:
        type: 事件名。
        origin: 原本是否处于全员禁言。
        current: 现在是否处于全员禁言。
        group: 全员禁言的群。
        operator: 操作者，为 None 表示 Bot 操作。
    """
    type: str = 'GroupMuteAllEvent'
    """事件名。"""
    origin: bool
    """原本是否处于全员禁言。"""
    current: bool
    """现在是否处于全员禁言。"""
    group: Group
    """全员禁言的群。"""
    operator: Optional[GroupMember]
    """操作者，为 None 表示 Bot 操作。"""


class GroupAllowAnonymousChatEvent(GroupEvent):
    """匿名聊天。

    Args:
        type: 事件名。
        origin: 原本是否允许匿名聊天。
        current: 现在是否允许匿名聊天。
        group: 匿名聊天状态改变的群。
        operator: 操作者，为 None 表示 Bot 操作。
    """
    type: str = 'GroupAllowAnonymousChatEvent'
    """事件名。"""
    origin: bool
    """原本是否允许匿名聊天。"""
    current: bool
    """现在是否允许匿名聊天。"""
    group: Group
    """匿名聊天状态改变的群。"""
    operator: Optional[GroupMember]
    """操作者，为 None 表示 Bot 操作。"""


class GroupAllowConfessTalkEvent(GroupEvent):
    """坦白说。

    Args:
        type: 事件名。
        origin: 原本是否允许坦白说。
        current: 现在是否允许坦白说。
        group: 坦白说状态改变的群。
        is_by_bot: 是否 Bot 进行该操作。
    """
    type: str = 'GroupAllowConfessTalkEvent'
    """事件名。"""
    origin: bool
    """原本是否允许坦白说。"""
    current: bool
    """现在是否允许坦白说。"""
    group: Group
    """坦白说状态改变的群。"""
    is_by_bot: bool
    """是否是 Bot 进行该操作。"""


class GroupAllowMemberInviteEvent(GroupEvent):
    """允许群员邀请好友加群。

    Args:
        type: 事件名。
        origin: 原本是否允许群员邀请好友加群。
        current: 现在是否允许群员邀请好友加群。
        group: 允许群员邀请好友加群状态改变的群。
        operator: 操作者，为 None 表示 Bot 操作。
    """
    type: str = 'GroupAllowMemberInviteEvent'
    """事件名。"""
    origin: bool
    """原本是否允许群员邀请好友加群。"""
    current: bool
    """现在是否允许群员邀请好友加群。"""
    group: Group
    """允许群员邀请好友加群状态改变的群。"""
    operator: Optional[GroupMember]
    """操作者，为 None 表示 Bot 操作。"""


class MemberJoinEvent(GroupEvent):
    """新人入群。

    Args:
        type: 事件名。
        member: 加入的群成员。
        group: 加入的群。
    """
    type: str = 'MemberJoinEvent'
    """事件名。"""
    member: GroupMember
    """加入的群成员。"""
    invitor: Optional[GroupMember]
    """邀请者。"""


class MemberLeaveEventKick(GroupEvent):
    """成员被踢出群（该成员不是Bot）。

    Args:
        type: 事件名。
        member: 被踢出的群成员。
        group: 事件发生的群。
        operator: 被踢出的群的管理员。
    """
    type: str = 'MemberLeaveEventKick'
    """事件名。"""
    member: GroupMember
    """被踢出的群成员。"""
    operator: Optional[GroupMember]
    """被踢出的群的管理员。"""


class MemberLeaveEventQuit(GroupEvent):
    """成员主动离群（该成员不是Bot）。

    Args:
        type: 事件名。
        member: 离群的群成员。
        group: 事件发生的群。
    """
    type: str = 'MemberLeaveEventQuit'
    """事件名。"""
    member: GroupMember
    """离群的群成员。"""


class MemberCardChangeEvent(GroupEvent):
    """群名片改动。

    Args:
        type: 事件名。
        origin: 原本名片。
        current: 现在名片。
        member: 改动的群成员。
        group: 事件发生的群。
    """
    type: str = 'MemberCardChangeEvent'
    """事件名。"""
    origin: str
    """原本名片。"""
    current: str
    """现在名片。"""
    member: GroupMember
    """改动的群成员。"""


class MemberSpecialTitleChangeEvent(GroupEvent):
    """群头衔改动（只有群主有操作权限）。

    Args:
        type: 事件名。
        origin: 原本头衔。
        current: 现在头衔。
        member: 头衔改动的群成员。
        group: 事件发生的群。
    """
    type: str = 'MemberSpecialTitleChangeEvent'
    """事件名。"""
    origin: str
    """原本头衔。"""
    current: str
    """现在头衔。"""
    member: GroupMember
    """头衔改动的群成员。"""


class MemberPermissionChangeEvent(GroupEvent):
    """成员权限改变（该成员不是Bot）。

    Args:
        type: 事件名。
        origin: 原本权限。
        current: 现在权限。
        member: 权限改变的群成员。
        group: 事件发生的群。
    """
    type: str = 'MemberPermissionChangeEvent'
    """事件名。"""
    origin: Permission
    """原本权限。"""
    current: Permission
    """现在权限。"""
    member: GroupMember
    """权限改变的群成员。"""


class MemberMuteEvent(GroupEvent):
    """群成员被禁言（该成员不是Bot）。

    Args:
        type: 事件名。
        duration_seconds: 禁言时间，单位为秒。
    """
    type: str = 'MemberMuteEvent'
    """事件名。"""
    duration_seconds: int
    """禁言时间，单位为秒。"""


class MemberUnmuteEvent(GroupEvent):
    """群成员被取消禁言（该成员不是Bot）。

    Args:
        type: 事件名。
        member: 被取消禁言的群成员。
        group: 事件发生的群。
    """
    type: str = 'MemberUnmuteEvent'
    """事件名。"""
    member: GroupMember
    """被取消禁言的群成员。"""
    operator: Optional[GroupMember]
    """被取消禁言的群管理员。"""


class MemberHonorChangeEvent(GroupEvent):
    """群员称号改变。

    Args:
        type: 事件名。
        member: 称号改变的群成员。
        action: 称号变化行为：achieve 获得称号，lose 失去称号。
        group: 事件发生的群。
        honor: 称号名称。
    """
    type: str = 'MemberHonorChangeEvent'
    """事件名。"""
    member: GroupMember
    """称号改变的群成员。"""
    action: Literal['achieve', 'lose']
    """称号变化行为：achieve 获得称号，lose 失去称号。"""
    honor: str
    """称号名称。"""


###############################
# Request Event


class RequestEvent(Event):
    """申请事件。

    Args:
        type: 事件名。
        event_id: 事件标识，响应该事件时的标识。
    """
    type: str
    """事件名。"""
    event_id: int
    """事件标识，响应该事件时的标识。"""
    from_id: int
    """申请人 QQ 号。"""
    group_id: int
    """申请人群号，可能为0。"""


class NewFriendRequestEvent(RequestEvent):
    """添加好友申请。

    Args:
        type: 事件名。
        event_id: 事件标识，响应该事件时的标识。
        from_id: 申请人 QQ 号。
        group_id: 申请人如果通过某个群添加好友，该项为该群群号；否则为0。
        nick: 申请人的昵称或群名片。
        message: 申请消息。
    """
    type: str = 'NewFriendRequestEvent'
    """事件名。"""
    event_id: int
    """事件标识，响应该事件时的标识。"""
    from_id: int
    """申请人 QQ 号。"""
    group_id: int
    """申请人如果通过某个群添加好友，该项为该群群号；否则为0。"""
    nick: str
    """申请人的昵称或群名片。"""
    message: str
    """申请消息。"""


class MemberJoinRequestEvent(RequestEvent):
    """用户入群申请（Bot需要有管理员权限）。

    Args:
        type: 事件名。
        event_id: 事件标识，响应该事件时的标识。
        from_id: 申请人 QQ 号。
        group_id: 申请人申请入群的群号。
        group_name: 申请人申请入群的群名称。
        nick: 申请人的昵称或群名片。
        message: 申请消息。
    """
    type: str = 'MemberJoinRequestEvent'
    """事件名。"""
    event_id: int
    """事件标识，响应该事件时的标识。"""
    from_id: int
    """申请人 QQ 号。"""
    group_id: int
    """申请人申请入群的群号。"""
    group_name: str
    """申请人申请入群的群名称。"""
    nick: str
    """申请人的昵称或群名片。"""
    message: str
    """申请消息。"""


class BotInvitedJoinGroupRequestEvent(RequestEvent):
    """Bot 被邀请入群申请。

    Args:
        type: 事件名。
        event_id: 事件标识，响应该事件时的标识。
        from_id: 邀请人 QQ 号。
        group_id: 被邀请进入群的群号。
        group_name: 被邀请进入群的群名称。
        nick: 邀请人（好友）的昵称。
        message: 邀请消息。
    """
    type: str = 'BotInvitedJoinGroupRequestEvent'
    """事件名。"""
    event_id: int
    """事件标识，响应该事件时的标识。"""
    from_id: int
    """邀请人 QQ 号。"""
    group_id: int
    """被邀请进入群的群号。"""
    group_name: str
    """被邀请进入群的群名称。"""
    nick: str
    """邀请人（好友）的昵称。"""
    message: str
    """邀请消息。"""


class NudgeEvent(Event):
    """头像戳一戳事件。

    Args:
        type: 事件名。
        from_id: 动作发出者的 QQ 号。
        target: 动作目标的 QQ 号。
        subject: 来源。
        action: 戳一戳类型。
        suffix: 自定义戳一戳内容。
    """
    type: str = "NudgeEvent"
    """事件名。"""
    from_id: int
    """动作发出者的 QQ 号。"""
    target: int
    """动作目标的 QQ 号。"""
    subject: Subject
    """来源。"""
    action: str
    """戳一戳类型。"""
    suffix: str
    """自定义戳一戳内容。"""


###############################
# Other Client Event


class OtherClientEvent(Event):
    """其它客户端事件。

    Args:
        type: 事件名。
        client: 其他设备。
    """
    type: str
    """事件名。"""
    client: Client
    """其他设备。"""


class ClientKind(int, Enum):
    """详细设备类型。"""
    ANDROID_PAD = 68104
    AOL_CHAOJIHUIYUAN = 73730
    AOL_HUIYUAN = 73474
    AOL_SQQ = 69378
    CAR = 65806
    HRTX_IPHONE = 66566
    HRTX_PC = 66561
    MC_3G = 65795
    MISRO_MSG = 69634
    MOBILE_ANDROID = 65799
    MOBILE_ANDROID_NEW = 72450
    MOBILE_HD = 65805
    MOBILE_HD_NEW = 71426
    MOBILE_IPAD = 68361
    MOBILE_IPAD_NEW = 72194
    MOBILE_IPHONE = 67586
    MOBILE_OTHER = 65794
    MOBILE_PC_QQ = 65793
    MOBILE_PC_TIM = 77313
    MOBILE_WINPHONE_NEW = 72706
    QQ_FORELDER = 70922
    QQ_SERVICE = 71170
    TV_QQ = 69130
    WIN8 = 69899
    WINPHONE = 65804


class OtherClientOnlineEvent(OtherClientEvent):
    """其它客户端上线事件。

    Args:
        type: 事件名。
        client: 其他设备。
        kind: 详细设备类型。
    """
    type: str = 'OtherClientOnlineEvent'
    """事件名。"""
    client: Client
    """其他设备。"""
    kind: Optional[ClientKind] = None
    """详细设备类型。"""


class OtherClientOfflineEvent(OtherClientEvent):
    """其它客户端下线事件。

    Args:
        type: 事件名。
        client: 其他设备。
    """
    type: str = 'OtherClientOfflineEvent'
    """事件名。"""
    client: Client
    """其他设备。"""


###############################
# Command Event


class CommandEvent(Event):
    """命令事件。

    Args:
        type: 事件名。
    """
    type: str
    """事件名。"""


class CommandExecutedEvent(CommandEvent):
    """命令被执行。

    Args:
        type: 事件名。
        name: 命令名称。
        friend: 发送命令的好友, 从控制台发送为 None。
        member: 发送命令的群成员, 从控制台发送为 None。
        args: 命令执行时的参数。
    """
    type: str = 'CommandExecutedEvent'
    """事件名。"""
    name: str
    """命令名称。"""
    friend: Optional[Friend]
    """发送命令的好友, 从控制台发送为 None。"""
    member: Optional[GroupMember]
    """发送命令的群成员, 从控制台发送为 None。"""
    args: MessageChain
    """命令执行时的参数。"""


###############################
# Message Event
class MessageEvent(Event):
    """消息事件。

    Args:
        type: 事件名。
        message_chain: 消息内容。
    """
    type: str
    """事件名。"""
    message_chain: MessageChain
    """消息内容。"""


class FriendMessage(MessageEvent):
    """好友消息。

    Args:
        type: 事件名。
        sender: 发送消息的好友。
        message_chain: 消息内容。
    """
    type: str = 'FriendMessage'
    """事件名。"""
    sender: Friend
    """发送消息的好友。"""
    message_chain: MessageChain
    """消息内容。"""


class GroupMessage(MessageEvent):
    """群消息。

    Args:
        type: 事件名。
        sender: 发送消息的群成员。
        message_chain: 消息内容。
    """
    type: str = 'GroupMessage'
    """事件名。"""
    sender: GroupMember
    """发送消息的群成员。"""
    message_chain: MessageChain
    """消息内容。"""
    @property
    def group(self) -> Group:
        return self.sender.group


class TempMessage(MessageEvent):
    """群临时消息。

    Args:
        type: 事件名。
        sender: 发送消息的群成员。
        message_chain: 消息内容。
    """
    type: str = 'TempMessage'
    """事件名。"""
    sender: GroupMember
    """发送消息的群成员。"""
    message_chain: MessageChain
    """消息内容。"""
    @property
    def group(self) -> Group:
        return self.sender.group


class StrangerMessage(MessageEvent):
    """陌生人消息。

    Args:
        type: 事件名。
        sender: 发送消息的人。
        message_chain: 消息内容。
    """
    type: str = 'StrangerMessage'
    """事件名。"""
    sender: Friend
    """发送消息的人。"""
    message_chain: MessageChain
    """消息内容。"""


class FriendSyncMessage(MessageEvent):
    """其他客户端发送的好友消息。

    Args:
        type: 事件名。
        subject: 发送消息的目标好友。
        message_chain: 消息内容。
    """
    type: str = 'FriendSyncMessage'
    """事件名。"""
    subject: Friend
    """发送消息的目标好友。"""
    message_chain: MessageChain
    """消息内容。"""


class GroupSyncMessage(MessageEvent):
    """其他客户端发送的群消息。

    Args:
        type: 事件名。
        subject: 发送消息的目标群组。
        message_chain: 消息内容。
    """
    type: str = 'GroupSyncMessage'
    """事件名。"""
    subject: Group
    """发送消息的目标群组。"""
    message_chain: MessageChain
    """消息内容。"""
    @property
    def group(self) -> Group:
        return self.subject


class TempSyncMessage(MessageEvent):
    """其他客户端发送的群临时消息。

    Args:
        type: 事件名。
        subject: 发送消息的目标群成员。
        message_chain: 消息内容。
    """
    type: str = 'TempSyncMessage'
    """事件名。"""
    subject: GroupMember
    """发送消息的目标群成员。"""
    message_chain: MessageChain
    """消息内容。"""
    @property
    def group(self) -> Group:
        return self.subject.group


class StrangerSyncMessage(MessageEvent):
    """其他客户端发送的陌生人消息。

    Args:
        type: 事件名。
        subject: 发送消息的目标。
        message_chain: 消息内容。
    """
    type: str = 'StrangerSyncMessage'
    """事件名。"""
    subject: Friend
    """发送消息的目标。"""
    message_chain: MessageChain
    """消息内容。"""


class OtherClientMessage(MessageEvent):
    """其他客户端消息。

    Args:
        type: 事件名。
        sender: 发送消息的人。
        message_chain: 消息内容。
    """
    type: str = 'OtherClientMessage'
    """事件名。"""
    sender: Client
    """发送消息的人。"""
    message_chain: MessageChain
    """消息内容。"""


__all__ = [
    'BotEvent', 'BotGroupPermissionChangeEvent',
    'BotInvitedJoinGroupRequestEvent', 'BotJoinGroupEvent',
    'BotLeaveEventActive', 'BotLeaveEventKick', 'BotMuteEvent',
    'BotOfflineEventActive', 'BotOfflineEventDropped', 'BotOfflineEventForce',
    'BotOnlineEvent', 'BotReloginEvent', 'BotUnmuteEvent', 'CommandEvent',
    'CommandExecutedEvent', 'ClientKind', 'Event', 'FriendEvent',
    'FriendInputStatusChangedEvent', 'FriendMessage', 'FriendNickChangedEvent',
    'FriendRecallEvent', 'GroupAllowAnonymousChatEvent',
    'GroupAllowConfessTalkEvent', 'GroupAllowMemberInviteEvent',
    'GroupEntranceAnnouncementChangeEvent', 'GroupEvent', 'GroupMessage',
    'GroupMuteAllEvent', 'GroupNameChangeEvent', 'GroupRecallEvent',
    'MemberCardChangeEvent', 'MemberHonorChangeEvent', 'MemberJoinEvent',
    'MemberJoinRequestEvent', 'MemberLeaveEventKick', 'MemberLeaveEventQuit',
    'MemberMuteEvent', 'MemberPermissionChangeEvent',
    'MemberSpecialTitleChangeEvent', 'MemberUnmuteEvent', 'MessageEvent',
    'NewFriendRequestEvent', 'NudgeEvent', 'OtherClientMessage',
    'RequestEvent', 'StrangerMessage', 'TempMessage'
]
