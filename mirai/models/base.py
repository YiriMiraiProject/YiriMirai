# -*- coding: utf-8 -*-
"""
此模块提供 YiriMirai 中使用的 pydantic 模型的基类。
"""
from pydantic import BaseModel


class MiraiBaseModel(BaseModel):
    """模型基类。

    启用了两项配置：
    1. 允许解析时传入额外的值，并将额外值保存在模型中。
    2. 允许通过别名访问字段。
    """
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

    class Config:
        extra = 'allow'
        allow_population_by_field_name = True
