from typing import List

from .base import *


class SchoolData(BaseData):
    id: int
    name: str
    imgurl: str
    register_count: int


class SchoolResData(BaseData):
    len: int = 0
    items: List[SchoolData] = [SchoolData(
        id=0,
        name='',
        imgurl='',
        register_count=0
    )]


class SchoolListResponse(BaseResponse):
    """
    register_count=0 是注册的人数
    """
    data: SchoolResData | BaseData = SchoolResData()
