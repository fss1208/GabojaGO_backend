# pip install fastapi uvicorn PyJWT

from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.favorite_table import FavoriteTable
from database.user_table import UserTable
from models.auth_model import UserModel
from models.auth_model import LoginRequestModel, LoginResponseModel

from library.JWT import AUTH_JWT
from library.LOG import LOG
from library.DB import DB

from datetime import datetime
import pandas as pd
import logging
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/register", summary="회원가입", response_model=UserModel)
def register(user_model: UserModel, request: Request):
    """
    회원가입
    - **strUserID**:str 필수 입력
    - **strUserPW**:str 필수 입력
    - **strName**:str 필수 입력
    - **strEmail**:str 필수 입력
    """    
    dt = datetime.now()
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", user_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, UserTable.TO_SELECT_MODEL_QUERY(user_model.strUserID))
            if (result != 0):
                connection.rollback()
                msg = f"사용자 ID 중복, id={user_model.strUserID}, result={result}"
                logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            #
            if (user_model.check_validation() == False):
                connection.rollback()
                msg = f"유효하지 않은 데이터, {user_model}"
                logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            #
            result = DB.EXECUTE(cursor, UserTable.TO_INSERT_QUERY(user_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, id={user_model.strUserID}, result={result}"
                logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            user_model.iPK = cursor.lastrowid
            #
            result = DB.EXECUTE(cursor, FavoriteTable.TO_INSERT_QUERY(user_model.iPK, "기본 즐겨찾기"))
            if (result != 1):
                connection.rollback()
                msg = f"기본 즐겨찾기 등록 실패, result={result}"
                logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            #
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, request_user, "성공", user_model.to_log(), dt))
    return user_model

@router.post("/login", summary="로그인", response_model=LoginResponseModel)
def login(request_model: LoginRequestModel, request: Request):
    """
    아이디와 비밀번호를 받아 유효한 경우 JWT 토큰을 반환
    - **strUserID**:str 필수 입력
    - **strUserPW**:str 필수 입력
    """
    dt = datetime.now()
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", request_model.strUserID))
    user_model = None
    dbname = os.getenv("DBNAME")
    with DB.CONNECT(dbname) as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, UserTable.TO_SELECT_LOGIN_QUERY(request_model))
            if (result != 1):
                msg = f"아이디 또는 비밀번호 불일치, {request_model.strUserID}"
                logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
                raise HTTPException(status_code=400, detail=msg)
            row_tuple = cursor.fetchone()
            user_model = UserTable.TO_MODEL(row_tuple)
    # 로그인 성공 시 토큰 생성
    token = AUTH_JWT.CREATE_TOKEN(user_model)
    response_model = LoginResponseModel(
        access_token = token,
        token_type = "bearer"
    )
    logger.info(LOG.TO_MESSAGE(request, request_user, "성공", user_model.to_log(), dt))
    return response_model

@router.get("/test", summary="사용자 인증 확인")
def test(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자 인증 테스트
    """
    user_model = AUTH_JWT.TO_USER_MODEL(auth)
    logger.debug(f"UserModel({user_model})")
    return {"message": f"{user_model.strName}님이 인증되었습니다! ({user_model.strUserID})"}
