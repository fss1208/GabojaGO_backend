from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.favorite_table import FavoriteTable
from models.favorite_model import FavoriteModel, FavoriteListModel
from library.JWT import AUTH_JWT
from library.LOG import LOG
from library.DB import DB

from datetime import datetime, timedelta
import logging
import json
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

#################################################################################################################

@router.post("/append", summary="즐겨찾기 추가", response_model=FavoriteModel)
def append_favorite(favorite_model: FavoriteModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청에 의한 즐겨찾기 추가
    - **FavoriteModel.strName: str** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", favorite_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            favorite_model.iUserFK = login_user.iPK
            result = DB.EXECUTE(cursor, FavoriteTable.TO_INSERT_QUERY(favorite_model.iUserFK, favorite_model.strName))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {favorite_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            favorite_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", favorite_model.to_log(), dt))
    return favorite_model

@router.post("/remove", summary="즐겨찾기 삭제", response_model=dict)
def remove_favorite(iFavoritePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청에 의한 즐겨찾기 삭제
    - **iFavoritePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iFavoritePK:{iFavoritePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteTable.TO_DELETE_QUERY(iFavoritePK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iFavoritePK": iFavoritePK}

@router.get("/list", summary="즐겨찾기 목록 조회", response_model=FavoriteListModel)
def list_favorite(request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 즐겨찾기 목록 조회
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청"))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteTable.TO_SELECT_LIST_QUERY(login_user.iPK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            favorite_list_model = FavoriteListModel(favorite_list=FavoriteTable.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{result}건", dt))
    return favorite_list_model
