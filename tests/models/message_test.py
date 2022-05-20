import time
from mirai.models.message import Plain, MessageChain, At

Source = MessageChain.Source


def test_create():
    chain = MessageChain(['str1', Plain('str2'), At(12345678)])
    assert chain.dict(exclude_none=True) == [
        {
            'type': 'Plain',
            'text': 'str1'
        }, {
            'type': 'Plain',
            'text': 'str2'
        }, {
            'type': 'At',
            'target': 12345678
        }
    ]


def test_parse():
    chain = MessageChain.parse_obj(
        [
            {
                'type': 'Plain',
                'text': 'str1'
            }, {
                'type': 'Plain',
                'text': 'str2'
            }, {
                'type': 'At',
                'target': 12345678
            }
        ]
    )
    assert chain == ['str1', Plain('str2'), At(12345678)]


def test_operate():
    chain = MessageChain([])
    chain += 'str1'
    chain += Plain('str2')
    chain += [At(12345678)]
    assert chain == ['str1', 'str2', At(12345678)]
    assert chain.exclude(At) == ['str1', 'str2']
    assert list(chain) == chain
    assert MessageChain.join(chain.exclude(At), chain[At]) == chain


def test_format():
    chain = MessageChain(['str1', Plain('str2'), At(12345678)])
    assert chain.as_mirai_code() == 'str1str2[mirai:at:12345678]'
    assert str(chain) == 'str1str2@12345678'
    assert eval(repr(chain)) == chain


def test_meta():
    source = MessageChain.parse_obj(
        [{
            'type': 'Source',
            'id': 0,
            'time': time.time(),
        }]
    ).source
    assert bool(source)
    quote = MessageChain.parse_obj(
        [
            {
                'type': 'Quote',
                'id': 1,
                'group_id': 0,
                'sender_id': 2,
                'target_id': 3,
                'origin': [{
                    'type': 'Plain',
                    'text': 'origin'
                }]
            }
        ]
    ).quote
    assert bool(quote)
    if source and quote:
        chain = MessageChain(
            [source, quote, 'str1',
             Plain('str2'), At(12345678)]
        )
        assert chain.source == source
        assert chain.quote == quote
        assert chain == ['str1', Plain('str2'), At(12345678)]
        assert str(chain) == 'str1str2@12345678'
