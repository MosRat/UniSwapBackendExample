from typing import List

from .base import *


class GoodsItem(BaseData):
    id: int
    name: str
    imgurl: str
    price: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    add_time: Optional[str] = None


class AddGoodsData(BaseData):
    imgs: list[str]
    name: str
    location: str
    price: str
    bio: str


class SearchResData(BaseData):
    len: int = 0
    items: List[GoodsItem] = [GoodsItem(
        id=114,
        name='xxxx',
        imgurl='https://cdn.xxxx.com'
    )]


class PromptResData(BaseData):
    len: int = 2
    items: List[GoodsItem] = [
        GoodsItem(id=1, name="crow",
                  imgurl='https://fastapi.tiangolo.com/img/favicon.png'),
        GoodsItem(id=2, name="mice",
                  imgurl='https://fastapi.tiangolo.com/img/favicon.png')]


class UserItemResData(BaseData):
    len: int = 0
    items: List[GoodsItem] = [GoodsItem(
        id=0,
        name='item name',
        imgurl='https://xxxxx',
        price=100,
        add_time="1y2m3d(一年、两个月、三天之前）"
    )]


class SearchResponse(BaseResponse):
    data: SearchResData | BaseData = SearchResData()


class PromptResponse(BaseResponse):
    data: PromptResData | BaseData = PromptResData()


class AddGoodsResponse(BaseResponse):
    pass


class UserItemsResponse(BaseResponse):
    data: UserItemResData | BaseData = UserItemResData()
