from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.image_table import ImageTable
from database.favorite.favorite_image_view import FavoriteImageView
from database.favorite.favorite_image_table import FavoriteImageTable
from models.favorite_model import FavoriteImageModel, FavoriteImageListModel

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

@router.post("/append", summary="즐겨찾기에 이미지 추가", response_model=FavoriteImageModel)
def append_favorite_image(favorite_image_model: FavoriteImageModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    즐겨찾기에 사용자가 요청한 이미지 추가
    - **FavoriteImageModel.iFavoriteFK: int** 필수 입력
    - **FavoriteImageModel.iImageFK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", favorite_image_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ImageTable.TO_SELECT_MODEL_QUERY(favorite_image_model.iImageFK))
            if (result != 1):
                msg = f"이미지가 존재하지 않아 등록 불가, {favorite_image_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            result = DB.EXECUTE(cursor, FavoriteImageTable.TO_INSERT_QUERY(favorite_image_model.iFavoriteFK, favorite_image_model.iImageFK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {favorite_image_model.to_log()}, count={result}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            favorite_image_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", favorite_image_model.to_log(), dt))
    return favorite_image_model

@router.post("/remove", summary="즐겨찾기에 이미지 삭제", response_model=dict)
def remove_favorite_image(iFavoriteImagePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    즐겨찾기에서 사용자가 요청한 이미지 삭제
    - **iFavoriteImagePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iFavoriteImagePK:{iFavoriteImagePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteImageTable.TO_DELETE_QUERY(iFavoriteImagePK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}, count={result}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iFavoriteImagePK": iFavoriteImagePK}

@router.get("/list", summary="즐겨찾기에 등록된 이미지 목록 조회", response_model=FavoriteImageListModel)
def list_favorite_image(iFavoritePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 즐겨찾기에 등록된 이미지 목록 조회
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청"))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, FavoriteImageView.TO_SELECT_LIST_QUERY(iFavoritePK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            favorite_image_list_model = FavoriteImageListModel(image_list=FavoriteImageView.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{result}건", dt))
    return favorite_image_list_model
