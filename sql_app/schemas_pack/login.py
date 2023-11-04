from .base import *


class LoginUserData(BaseData):
    userinfo: str
    pwd: str


class LoginWxData(BaseData):
    userinfo: str


class LoginData(BaseData):
    type: Literal['email', 'phone', 'weixin']
    data: LoginUserData | LoginWxData


class LoginResData(BaseData):
    token: str
    username: str


class LoginResponse(BaseResponse):
    data: LoginResData | BaseData
