from pydantic import BaseModel
from typing import Literal, Optional


class BaseData(BaseModel):
    pass


class PhoneNumberData(BaseData):
    phonenumber: str


class IdData(BaseData):
    id: str


class EmailData(BaseData):
    email: str


class SearchDetailData(BaseData):
    """
    time时间表示多少时间以内
    """
    area: Literal['all', 'A1', 'B1', 'C1'] = 'all'
    type: Literal['all', 'type1', 'type2', 'type3'] = 'all'
    time: Literal['all', 'month', 'week', 'three days', 'today'] = 'all'


class SearchData(BaseData):
    keywords: str
    details: SearchDetailData = SearchDetailData()


class PromptData(BaseData):
    keywords: str


class UserNameData(BaseData):
    username: str


class UserIdData(BaseData):
    pass


class UserTokenData(BaseData):
    token: str


class UserUIDData(BaseData):
    uid: str | None = None


class UserUpdateData(BaseData):
    uid: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    school: Optional[str] = None
    gender: Optional[str] = None
    profile_bg: Optional[str] = None
    is_following: Optional[bool] = None


class UserInfoResData(BaseData):
    username: str
    phone: str
    email: str
    avatar: str
    school: str
    gender: Literal['male', 'female']
    is_following: Optional[bool] = None
    profile_bg: str
    follower_count: int
    following_count: int


class UserProfileResData(BaseData):
    username: str
    avatar: str
    school: str
    profile_bg: str
    is_following: bool
    follower_count: int
    following_count: int


class UploadMediaResData(BaseData):
    src: str


class BaseResponse(BaseModel):
    status: int = 200
    data: BaseData = BaseData()
    msg: str = "ok"


class NullResponse(BaseResponse):
    pass


class UploadMediaResponse(BaseResponse):
    data: UploadMediaResData | BaseData = UploadMediaResData(src="https://xxxx")


class UserInfoResponse(BaseResponse):
    data: UserInfoResData | BaseData = UserInfoResData(username="xxx",
                                                       phone="111",
                                                       email="xxx@qq.com",
                                                       avatar="https://xxxx",
                                                       school="xxx",
                                                       gender="male",
                                                       profile_bg='https://xxxx',
                                                       follower_count=1,
                                                       following_count=1)


class UserProfileResponse(BaseResponse):
    data: UserUIDData | BaseData = UserProfileResData(username="xxx",
                                                      avatar="https://xxxx",
                                                      school="xxx",
                                                      is_following=False,
                                                      profile_bg='https://xxxx',
                                                      follower_count=1,
                                                      following_count=1
                                                      )


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
