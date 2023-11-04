from .base import *


class SignUpInfoData(BaseData):
    username: str
    pwd: str
    userinfo: str


class SignUpData(BaseData):
    data: SignUpInfoData
    type: Literal['email', 'phone']


class SignUpResData(BaseData):
    pass


class SignUpResponse(BaseResponse):
    data: SignUpResData
