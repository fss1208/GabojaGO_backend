from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.favorite.favorite_location_view import FavoriteLocationView
from database.favorite.favorite_location_table import FavoriteLocationTable
from models.favorite_model import FavoriteLocationModel, FavoriteLocationListModel
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

@router.post("/append", summary="즐겨찾기에 장소 추가", response_model=FavoriteLocationModel)
def append_favorite_location(favorite_location_model: FavoriteLocationModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청에 의한 즐겨찾기에 장소 추가
    - **FavoriteLocationModel.iFavoriteFK: int** 필수 입력
    - **FavoriteLocationModel.iLocationFK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", favorite_location_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteLocationTable.TO_INSERT_QUERY(favorite_location_model.iFavoriteFK, favorite_location_model.iLocationFK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {favorite_location_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            favorite_location_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", favorite_location_model.to_log(), dt))
    return favorite_location_model

@router.post("/remove", summary="즐겨찾기에 장소 삭제", response_model=dict)
def remove_favorite_location(iFavoriteLocationPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청에 의한 즐겨찾기에 장소 삭제
    - **iFavoriteLocationPK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iFavoriteLocationPK:{iFavoriteLocationPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteLocationTable.TO_DELETE_QUERY(iFavoriteLocationPK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iFavoriteLocationPK": iFavoriteLocationPK}

@router.get("/list", summary="즐겨찾기에 등록된 장소 목록 조회", response_model=FavoriteLocationListModel)
def list_favorite_location(iFavoritePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 즐겨찾기에 등록된 장소 목록 조회
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청"))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteLocationView.TO_SELECT_LIST_QUERY(iFavoritePK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            favorite_location_list_model = FavoriteLocationListModel(location_list=FavoriteLocationView.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{result}건", dt))
    return favorite_location_list_model
