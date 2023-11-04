import sys
from typing import Annotated

from fastapi import Depends, FastAPI, UploadFile, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas_pack, models
from .database import SessionLocal, engine
from .status import Status
from docs.fmt import format_doc

VERSION = '0.3.0'

tags_metadata = [
    {
        "name": "user",
        "description": "## 用户有关的接口",
    },
    {
        "name": "goods",
        "description": "## 商品有关的接口",
    },
    {
        "name": "school",
        "description": "## 学校有关的接口",
    },
    {
        "name": "media",
        "description": "## 资源文件有关的接口，将来可能用第三方存储服务实现？",
    },
]

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title='Uniswap API Docs',
              description=format_doc(VERSION),
              openapi_tags=tags_metadata,
              version=VERSION
              )
app.mount("/doc", StaticFiles(directory="docs"), name="doc")
app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/user/phone_exist', response_model=schemas_pack.NullResponse, tags=['user'])
def user_exist_phone(data: schemas_pack.PhoneNumberData, db: Session = Depends(get_db)):
    """
    使用手机号检查用户是否存在，存在返回`SUCCESS`，不存在返回`NOEXIST`

    请求体数据：`PhoneNumberData`，返回：`NullResponse`
    """
    return schemas_pack.NullResponse(
        **(Status.SUCCESS if crud.get_user_by_phone(db, phone=data.phonenumber) else Status.NOTFOUND))


@app.post('/user/mail_exist', response_model=schemas_pack.NullResponse, tags=['user'])
def user_exist_email(data: schemas_pack.EmailData, db: Session = Depends(get_db)):
    """
    使用邮箱检查用户是否存在，存在返回`SUCCESS`，不存在返回`NOEXIST`

    请求体数据：`EmailData`，返回：`NullResponse`
    """
    return schemas_pack.NullResponse(
        **(Status.SUCCESS if crud.get_user_by_email(db, email=data.email) else Status.NOTFOUND))


@app.post('/user/signup', response_model=schemas_pack.SignUpResponse, tags=['user'])
def user_signup(data: schemas_pack.SignUpData, db: Session = Depends(get_db)):
    """
    用户注册api，四个参数：`username`:用户名、`type`:注册类型`[phone|email]`、`userinfo`:邮箱/手机号、`pwd`:密码，前端已做好校验,，成功返回`SUCCESS`，失败返回`FAIL`，在data中返回token

    请求体数据：`SignUpData`，返回：`SignUpResponse`
    """
    try:
        if data.type == "email":
            user_id = crud.create_user(db=db,
                                       user=schemas_pack.UserCreate(id=data.data.username, email=data.data.userinfo,
                                                                    password=data.data.pwd))
        elif data.type == "phone":
            user_id = crud.create_user(db=db,
                                       user=schemas_pack.UserCreate(id=data.data.username, phone=data.data.userinfo,
                                                                    password=data.data.pwd))
        else:
            user_id = {"_id": -1}
    except Exception as e:
        print(e, e.args, e.__traceback__, sys.stderr)
        return schemas_pack.SignUpResponse(**Status.INTERNALERROR, data=schemas_pack.SignUpResData())
    return schemas_pack.SignUpResponse(**Status.SUCCESS, data=schemas_pack.SignUpResData())


@app.post('/user/login', response_model=schemas_pack.LoginResponse, tags=['user'])
def user_login(data: schemas_pack.LoginData, db: Session = Depends(get_db)):
    """
    用户登录api

    `type:['email'|'phone'|'weixin']` ：指定使用手机号、邮箱或者微信登录

    `data` ： 参数传入登录凭据,如果是手机或邮箱含有用户名`username`和注册信息`userinfo`,wx只有`userinfo`

    `userinfo` ：手机号或者邮箱,如果是微信登录那么请求体userinfo代表授权码

    `pwd` ：未加密密码

    成功返回`SUCCESS`，失败返回`FAIL`，在返回中(data)返回token和用户名

    请求体数据：`LoginData`，返回：`LoginResponse`
    """
    try:
        print(data.data.userinfo, data.data.pwd)
        if data.type == "phone":
            res = crud.check_user_by_phone(db, data.data.userinfo, data.data.pwd)
        elif data.type == "email":
            res = crud.check_user_by_email(db, data.data.userinfo, data.data.pwd)
        else:
            return schemas_pack.LoginResponse(**Status.SUCCESS,
                                              data=schemas_pack.LoginResData(token=str(-2), username=str(-2)))
        if res:
            print(res.id, res.id)
            return schemas_pack.LoginResponse(**Status.SUCCESS,
                                              data=schemas_pack.LoginResData(token=res.id, username=str(res.id)))
        return schemas_pack.LoginResponse(**Status.FAIL, data=schemas_pack.LoginResData(token="-1", username="-1"))
    except Exception as e:
        print(e, e.args, e.__traceback__, sys.stderr)
        return schemas_pack.LoginResponse(**Status.INTERNALERROR,
                                          data=schemas_pack.BaseData())


@app.get('/user/info', response_model=schemas_pack.UserInfoResponse, tags=['user'])
def get_user_info(token: Annotated[str, Header()],
                  db: Session = Depends(get_db)):
    """
    通过token获取详细用户信息，请求头携带token，返回昵称、性别、头像地址、邮箱、用户名等,token过期返回`UNAUTHORIZED`

    请求体数据：无，返回：`UserInfoResponse`
    """
    user = 1
    if user:
        return schemas_pack.UserInfoResponse(**Status.SUCCESS)
    else:
        return schemas_pack.UserInfoResponse(**Status.NOTFOUND, data=schemas_pack.BaseData())


@app.post('/user/profile', response_model=schemas_pack.UserProfileResponse, tags=['user'])
def get_user_profile(token: Annotated[str, Header()], data: schemas_pack.UserUIDData, db: Session = Depends(get_db)):
    """
    查看别人主页时的请求数据，token代表的用户（app使用者）获取uid用户（被查看信息）的信息，携带token、uid，返回昵称、头像地址、是否关注、关注人数和被关注人数等

    请求体数据：`UserTokenData`，返回：`UserInfoResponse`
    """
    user = 1
    if user:
        return schemas_pack.UserProfileResponse(**Status.SUCCESS)
    else:
        return schemas_pack.UserProfileResponse(**Status.NOTFOUND, data=schemas_pack.BaseData())


@app.post('/user/update', response_model=schemas_pack.UserInfoResponse, tags=['user'])
def update_user_info(token: Annotated[str, Header()], data: schemas_pack.UserUpdateData, db: Session = Depends(get_db)):
    """
    更新用户信息，请求头携带token、所有参数均可选但至少一个，其中uid用于follow状态改变和is_follow绑定。返回改变后的用户信息

    请求体数据：`UserUpdateData`，返回：`UserInfoResponse`
    """
    user = 1
    if user:
        return schemas_pack.UserInfoResponse(**Status.SUCCESS)
    else:
        return schemas_pack.UserInfoResponse(**Status.NOTFOUND, data=schemas_pack.BaseData())


@app.get('/user/items', response_model=schemas_pack.UserItemsResponse, tags=['user'])
def get_user_items(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    """
    通过token获取用户上传物品，请求头携带token，返回物品项计数和物品项列表，每个物品项包括id、价格、图片、上传时间

    请求体数据：无，返回：`UserItemsResponse`
    """
    user = 1
    if user:
        return schemas_pack.UserItemsResponse(**Status.SUCCESS, data=schemas_pack.UserItemResData(
            len=3,
            items=[schemas_pack.GoodsItem(**i) for i in [
                {
                    'id': 1,
                    'imgurl': "../../static/image/sample.png",
                    'name': "200BYTE,OR HIDE?",
                    'price': 100,
                    'add_time': "13h"
                },
                {
                    'id': 2,
                    'imgurl': "../../static/image/sample.png",
                    'name': "sofa",
                    'price': 120,
                    'add_time': "13h"
                },
                {
                    'id': 3,
                    'imgurl': "../../static/image/sample.png",
                    'name': "121",
                    'price': 220,
                    'add_time': "13h"
                }
            ]]
        ))
    else:
        return schemas_pack.UserItemsResponse(**Status.NOTFOUND, data=schemas_pack.BaseData())


@app.post('/goods/search', response_model=schemas_pack.SearchResponse, tags=['goods'])
def get_search_result(token: Annotated[str, Header()], data: schemas_pack.SearchData, db: Session = Depends(get_db)):
    """
    搜索接口，关键词`keywords`查找相关物品,`detail`是筛选词，见`SearchDetailData`，返回物品列表和长度`SearchResponse`，物品类型见`GoodsItem`

    请求体数据：`SearchData`，返回：`SearchResponse`
    """
    try:
        return schemas_pack.SearchResponse(data=schemas_pack.SearchResData(len=2, items=[
            schemas_pack.GoodsItem(id=1, name="crow",
                                   imgurl='https://fastapi.tiangolo.com/img/favicon.png'),
            schemas_pack.GoodsItem(id=2, name="mice",
                                   imgurl='https://fastapi.tiangolo.com/img/favicon.png')]),
                                           **Status.SUCCESS)
    except Exception as e:
        print(e)
        return schemas_pack.SearchResponse(data=schemas_pack.BaseData(), **Status.FAIL)


@app.post('/goods/prompt', response_model=schemas_pack.PromptResponse, tags=['goods'])
def get_prompt_result(token: Annotated[str, Header()], data: schemas_pack.PromptData, db: Session = Depends(get_db)):
    """
    搜索提示词接口，关键词`keywords`推荐相关物品,用户`token`表明用户身份`

    请求体数据：`PromptData`，返回：`PromptResponse`
    """
    try:
        return schemas_pack.PromptResponse(**Status.SUCCESS)
    except Exception as e:
        print(e)
        return schemas_pack.PromptResponse(data=schemas_pack.BaseData(), **Status.FAIL)


@app.get('/school/list', response_model=schemas_pack.SchoolListResponse, tags=['school'])
def get_goods_list(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    """
    查询学校列表，不发送数据，应该返回`SchoolListResponse`，

    请求体数据：`BaseData`，返回：`SchoolListResponse`
    """
    try:
        return schemas_pack.SchoolListResponse(data=schemas_pack.SchoolResData(len=8, items=[
            schemas_pack.SchoolData(**i) for i in [
                {"id": 1, "imgurl": "../../static/image/sample.png", "register_count": 100,
                 "name": "University of Combridge"},
                {"id": 2, "imgurl": "../../static/image/sample.png", "register_count": 10,
                 "name": "University of Oxford"},
                {"id": 3, "imgurl": "../../static/image/sample.png", "register_count": 8,
                 "name": "Imperial College London"},
                {"id": 4, "imgurl": "../../static/image/sample.png", "register_count": 8,
                 "name": "University College London"},
                {"id": 5, "imgurl": "../../static/image/sample.png", "register_count": 100,
                 "name": "University of Combridge"},
                {"id": 6, "imgurl": "../../static/image/sample.png", "register_count": 10,
                 "name": "University of Oxford"},
                {"id": 7, "imgurl": "../../static/image/sample.png", "register_count": 8,
                 "name": "Imperial College London"},
                {"id": 8, "imgurl": "../../static/image/sample.png", "register_count": 8,
                 "name": "University College London"}]

        ]),
                                               **Status.SUCCESS)
    except Exception as e:
        print(e, file=sys.stderr)
        return schemas_pack.SchoolListResponse(data=schemas_pack.BaseData(), **Status.FAIL)


@app.post('/goods/add', response_model=schemas_pack.AddGoodsResponse, tags=['goods'])
def add_goods(token: Annotated[str, Header()], data: schemas_pack.AddGoodsData
              , db: Session = Depends(get_db)
              ):
    """
    上传物品信息，imgs图片或视频，下面名字、位置、价格、简介以表单数据传输

    请求：`AddGoodsData` 返回：`AddGoodsResponse`
    """
    print(*(i for i in data))
    return schemas_pack.AddGoodsResponse()


@app.post('/media/image', response_model=schemas_pack.UploadMediaResponse, tags=['media'])
def upload_images(token: Annotated[str, Header()], image: UploadFile, db: Session = Depends(get_db)):
    """
    上传图片，以表单数据传输,返回获取图片的url，这个url不一定是我们自己的，可以是COS之类的？

    请求：表单数据,携带图片文件img 返回：`UploadMediaResponse`
    """
    return schemas_pack.UploadMediaResponse(**Status.SUCCESS)

# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)
#
#
# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users
#
#
# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: str, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
#
#
# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#         user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)
#
#
# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
