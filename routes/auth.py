# pip install fastapi uvicorn PyJWT

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.auth_model import UserModel, LoginRequestModel, LoginResponseModel
from library.JWT import AuthJWT
from library.DB import DB
import pandas as pd
import logging
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/register", summary="회원가입", response_model=UserModel)
def register(user_model: UserModel):
    logger.debug(f"Request Body {user_model.model_dump()}")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, user_model.select_query())
            if (result != 0):
                raise HTTPException(status_code=401, detail=f"사용자 ID 중복! (id={user_model.id}, result={result})")
            if (user_model.check_validation() == False):
                raise HTTPException(status_code=401, detail="유효하지 않은 데이터!")
            result = DB.EXECUTE(cursor, user_model.insert_query())
            if (result != 1):
                raise HTTPException(status_code=401, detail=f"회원정보 추가 실패! (id={user_model.id}, result={result})")
            connection.commit()
            result = DB.EXECUTE(cursor, user_model.select_query())
            if (result != 1):
                raise HTTPException(status_code=401, detail=f"회원정보 찾기 실패! (id={user_model.id}, result={result})")
            rows_tuple = cursor.fetchall()
            user_model = UserModel(row=rows_tuple[0])
            return user_model.model_dump()

@router.post("/login", summary="로그인", response_model=LoginResponseModel)
def login(user: LoginRequestModel):
    """
    아이디와 비밀번호를 받아 유효한 경우 JWT 토큰을 반환
    - **id**: 필수 입력
    - **pw**: 필수 입력
    """
    user_model = None
    name = os.getenv("DBNAME")
    logger.debug(f"Request Body ({user})")
    with DB.CONNECT(name) as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, user.check_query())
            if (result == 0):
                raise HTTPException(status_code=401, detail="아이디 또는 비밀번호 불일치!")
            rows_tuple = cursor.fetchall()
            user_model = UserModel(row=rows_tuple[0])
            logger.debug(f"UserModel({user_model})")
    # 로그인 성공 시 토큰 생성
    token = AuthJWT.create_token(user_model)
    response = LoginResponseModel(
        access_token = token,
        token_type = "bearer"
    )
    return response.model_dump()

@router.get("/test", summary="사용자 인증 확인")
def test(auth: HTTPAuthorizationCredentials = Depends(security)):
    user_model = AuthJWT.get_user_model(auth)
    logger.debug(f"UserModel({user_model})")
    return {"message": f"환영합니다! ({user_model})"}
