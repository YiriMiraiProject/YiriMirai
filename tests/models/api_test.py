import asyncio
from mirai.api_provider import ApiProvider, Method
from mirai.models.api import ApiModel
from mirai.models.message import MessageChain, Plain

msg = ['Hello', Plain('World!')]


class FakeAPI(ApiProvider):
    async def call_api(self, api: str, method: Method = Method.GET, **params):
        if api == 'sendFriendMessage':
            chain = params.get('messageChain')
            assert isinstance(chain, list)
            assert MessageChain.parse_obj(chain) == msg
            return {'code': 0, 'msg': '', 'messageId': 1}

    def __getattr__(self, api: str):
        api_type = ApiModel.get_subtype(api)
        return api_type.Proxy(self, api_type)


def test_send_message():
    bot = FakeAPI()
    assert asyncio.run(bot.send_friend_message(123, msg)) == 1