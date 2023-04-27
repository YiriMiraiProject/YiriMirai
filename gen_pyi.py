# -*- coding: utf-8 -*-
# type: ignore

import pdoc
import textwrap
import re
import mirai
# from objprint import op

def indent(text, n):
    return textwrap.indent(text, ' ' * n * 4)


module = pdoc.Module(mirai.models.api)
s = ""
for api in sorted(
    set(mirai.models.api.ApiModel.__indexes__.values()),
    key=lambda x: x.__name__
):
    c = module.find_class(api)
    print('正在处理：', api.__name__)
    anno = api.__annotations__
    # op(c)
    params = ', '.join(
        '{}: {}'.format(
            k, c.doc[k].type_annotation().replace("\xa0", "") + (
                "" if api.__fields__[k].
                required else f" = {api.__fields__[k].default!r}"
            )
        ) for k, v in anno.items() if k[0] != '_' and k != 'Info'
    )

    params_doc = '\n'.join(
        '{} (`{}`): {}'.format(
            k, c.doc[k].type_annotation().replace("\xa0", ""),
            c.doc[k].docstring.rstrip('。') + (
                "。" if api.__fields__[k].
                required else f"，默认值 {api.__fields__[k].default!r}。"
            )
        ) for k, v in anno.items() if k[0] != '_' and k != 'Info'
    )

    s += f'''
    # {api.__name__}
'''

    try:
        response_type = api.Info.response_type
        response_type_name = response_type.__qualname__
    except AttributeError:
        response_type_name = 'None'

    try:
        response_post_type = api.Info.response_type_post
        response_post_type_name = response_post_type.__name__
    except AttributeError:
        response_post_type_name = 'None'

    print(response_type_name)

    if issubclass(api, mirai.models.api.ApiGet):
        s += f'''
    @type_check_only
    class __{api.__name__}Proxy():
        async def get(self, {params}) -> {response_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
        async def __call__(self, {params}) -> {response_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
'''
    elif issubclass(api, mirai.models.api.ApiPost):
        s += f'''
    @type_check_only
    class __{api.__name__}Proxy():
        async def set(self, {params}) -> {response_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
        async def __call__(self, {params}) -> {response_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
'''
    elif issubclass(api, mirai.models.api.ApiRest):
        s += f'''
    @type_check_only
    class __{api.__name__}Proxy():
        async def get(self, {params}) -> {response_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
        async def set(self, {params}) -> {response_post_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
        async def __call__(self, {params}) -> {response_type_name}:
            """{c.docstring}
            Args:
{indent(params_doc, 4)}
            """
'''

    s += f'''
    @property
    def {api.Info.alias}(self) -> __{api.__name__}Proxy:
       """{c.docstring}
        Args:
{indent(params_doc, 3)}
        """
'''

s = re.sub(r'Args:(\n\s*)*\s*"""', '"""', s)
s = re.sub(r'"""(.+)(\n\s*)+\s*"""', r'"""\1"""', s)
s = s.replace('NoneType', 'None').replace(', )', ')')
s = s.replace('pathlib.Path', 'Path')
s = re.sub(r'mirai\.(\w+\.)*(\w)', lambda m: m.group(2), s)

with open('./mirai/bot.pyi', 'r', encoding='utf-8') as f:
    pyi = f.read()
    p = '### 以下为自动生成 ###'
    s = pyi[:pyi.find(p) + len(p)] + s

with open('./mirai/bot.pyi', 'w', encoding='utf-8') as f:
    f.write(s)