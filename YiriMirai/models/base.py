from pydantic import BaseModel

class MiraiBaseModel(BaseModel):
    class Config:
        extra = 'allow'
        allow_population_by_field_name = True