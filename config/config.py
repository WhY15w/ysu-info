from pydantic import BaseModel


class Config(BaseModel):
    # 配置项,请根据需要修改
    username: str = ""
    password: str = ""
    pushkey: str = ""
