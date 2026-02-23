# pip install fastapi uvicorn PyJWT

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.auth_model import LoginRequestModel, LoginResponseModel
from models.auth_model import UserModel, UserTable
from library.JWT import AUTH_JWT
from library.DB import DB
import pandas as pd
import logging
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/register", summary="회원가입", response_model=UserModel)
def register(user_model: UserModel):
    """
    회원가입
    - **id**: 필수 입력
    - **pw**: 필수 입력
    - **name**: 필수 입력
    - **email**: 필수 입력
    """    
    logger.info(f"회원가입 요청 ({user_model})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, UserTable.TO_SELECT_MODEL_QUERY(user_model))
            if (result != 0):
                msg = f"회원가입 실패! (사용자 ID 중복 : id={user_model.id}, result={result})"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            if (user_model.check_validation() == False):
                msg = f"회원가입 실패! (유효하지 않은 데이터 : {user_model})"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            result = DB.EXECUTE(cursor, UserTable.TO_INSERT_QUERY(user_model))
            if (result != 1):
                msg = f"회원가입 실패! (DB 등록 실패 : id={user_model.id}, result={result})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
            user_model.pk = cursor.lastrowid
    logger.info(f"회원가입 성공 ({user_model})")
    return user_model

@router.post("/login", summary="로그인", response_model=LoginResponseModel)
def login(request_model: LoginRequestModel):
    """
    아이디와 비밀번호를 받아 유효한 경우 JWT 토큰을 반환
    - **id**: 필수 입력
    - **pw**: 필수 입력
    """
    logger.info(f"로그인 요청 ({request_model.id})")
    logger.debug(f"Request ({request_model})")
    user_model = None
    dbname = os.getenv("DBNAME")
    with DB.CONNECT(dbname) as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, UserTable.TO_SELECT_LOGIN_QUERY(request_model))
            if (result == 0):
                msg = f"로그인 실패! (아이디 또는 비밀번호 불일치 : {request_model.id})"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            rows_tuple = cursor.fetchall()
            user_model = UserTable.TO_MODEL(rows_tuple[0])
            logger.debug(f"UserModel({user_model})")
    # 로그인 성공 시 토큰 생성
    token = AUTH_JWT.CREATE_TOKEN(user_model)
    response_model = LoginResponseModel(
        access_token = token,
        token_type = "bearer"
    )
    logger.info(f"로그인 성공 ({user_model.id} {user_model.name})")
    return response_model

@router.get("/test", summary="사용자 인증 확인")
def test(auth: HTTPAuthorizationCredentials = Depends(security)):
    user_model = AUTH_JWT.TO_USER_MODEL(auth)
    logger.debug(f"UserModel({user_model})")
    return {"message": f"{user_model.name}님이 인증되었습니다! ({user_model.id})"}
